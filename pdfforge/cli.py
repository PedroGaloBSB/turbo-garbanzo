"""
Interface de linha de comando do PDFForge.

Uso:
    pdfforge extract arquivo.pdf -o saida.txt
    pdfforge convert arquivo.pdf --format markdown -o saida.md
    pdfforge info arquivo.pdf
    pdfforge batch ./pdfs/ --output ./saida/
"""

import click
from pathlib import Path
import json


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """PDFForge - Ferramenta de Manipulação de PDFs Open Source"""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Arquivo de saída')
@click.option('--clean', is_flag=True, help='Aplicar limpeza no texto')
def extract(input_file, output, clean):
    """Extrai texto de um PDF."""
    from .core.document import PDFDocument
    from .core.cleaner import DocumentCleaner
    
    try:
        with PDFDocument(input_file) as doc:
            if clean:
                cleaner = DocumentCleaner(doc)
                text = cleaner.clean()
            else:
                text = doc.extract_text()
            
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(text)
                click.echo(f"Texto extraído para: {output}")
            else:
                click.echo(text)
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-f', '--format', 'fmt', type=click.Choice(['text', 'markdown', 'json', 'html']), 
              default='text', help='Formato de saída')
@click.option('-o', '--output', type=click.Path(), help='Arquivo de saída')
@click.option('--pretty', is_flag=True, help='Formatação bonita (para JSON)')
def convert(input_file, fmt, output, pretty):
    """Converte PDF para outro formato."""
    from .core.document import PDFDocument
    from .formats import ExportManager
    
    try:
        with PDFDocument(input_file) as doc:
            if not output:
                output = Path(input_file).stem + '.' + fmt
            
            manager = ExportManager()
            
            kwargs = {}
            if fmt == 'json' and pretty:
                kwargs['pretty'] = True
            
            manager.export(doc, output, format=fmt, **kwargs)
            click.echo(f"Convertido para: {output}")
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def info(input_file):
    """Mostra informações sobre um PDF."""
    from .utils.helpers import get_pdf_info
    
    try:
        info = get_pdf_info(input_file)
        
        click.echo(f"\n📄 Arquivo: {info['file_name']}")
        click.echo(f"📊 Tamanho: {info['file_size']:,} bytes")
        click.echo(f"📑 Páginas: {info['page_count']}")
        click.echo(f"📝 Tipo: {info['type']}")
        click.echo(f"🔒 Criptografado: {'Sim' if info['is_encrypted'] else 'Não'}")
        
        if info['metadata']:
            click.echo("\n📋 Metadados:")
            for key, value in info['metadata'].items():
                if value:
                    click.echo(f"   {key}: {value}")
        
        click.echo("\n📊 Detalhes das páginas:")
        for page in info['pages'][:5]:  # Mostra primeiras 5 páginas
            click.echo(
                f"   Página {page['number']}: "
                f"{page['width']:.0f}x{page['height']:.0f}, "
                f"{page['text_length']} chars, "
                f"{page['image_count']} imagens"
            )
        
        if len(info['pages']) > 5:
            click.echo(f"   ... e mais {len(info['pages']) - 5} páginas")
            
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', type=click.Path(), help='Diretório de saída')
@click.option('-f', '--format', 'fmt', type=click.Choice(['text', 'markdown', 'json', 'html']),
              default='json', help='Formato de saída')
@click.option('--recursive', is_flag=True, help='Buscar recursivamente')
@click.option('--workers', '-w', type=int, default=4, help='Número de workers')
def batch(input_dir, output_dir, fmt, recursive, workers):
    """Processa múltiplos PDFs em lote."""
    from .utils.batch import BatchProcessor
    
    try:
        processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output_dir
        )
        
        pdf_files = processor.find_pdfs(recursive=recursive)
        
        if not pdf_files:
            click.echo("Nenhum PDF encontrado.")
            return
        
        click.echo(f"Encontrados {len(pdf_files)} PDFs.")
        
        if output_dir:
            exported = processor.export_all(
                pdf_files=pdf_files,
                format=fmt,
                output_dir=output_dir,
                max_workers=workers
            )
            click.echo(f"Exportados {len(exported)} arquivos para: {output_dir}")
        else:
            results = processor.process(
                pdf_files=pdf_files,
                max_workers=workers
            )
            
            success = sum(1 for r in results if r.get('success'))
            click.echo(f"Processados {success}/{len(results)} arquivos com sucesso")
            
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


@cli.command()
@click.argument('output_file', type=click.Path())
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
def merge(output_file, input_files):
    """Mescla múltiplos PDFs em um único arquivo."""
    import fitz
    
    if len(input_files) < 2:
        click.echo("É necessário pelo menos 2 arquivos para mesclar.", err=True)
        return
    
    try:
        merged_doc = fitz.open()
        
        for pdf_file in input_files:
            doc = fitz.open(pdf_file)
            merged_doc.insert_pdf(doc)
            doc.close()
        
        merged_doc.save(output_file)
        merged_doc.close()
        
        click.echo(f"Mesclados {len(input_files)} arquivos em: {output_file}")
        
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--images-only', is_flag=True, help='Extrair apenas imagens')
@click.option('-o', '--output-dir', type=click.Path(), help='Diretório de saída')
def images(input_file, images_only, output_dir):
    """Extrai imagens de um PDF."""
    from .core.document import PDFDocument
    
    try:
        with PDFDocument(input_file) as doc:
            extractor = doc.extract_images()
            
            if images_only or output_dir:
                output_dir = Path(output_dir) if output_dir else Path("images")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                saved = extractor.save_images(output_dir)
                click.echo(f"Salvas {len(saved)} imagens em: {output_dir}")
            else:
                # Mostra informações das imagens
                click.echo(f"\n📷 Imagens encontradas: {len(extractor)}")
                for img in extractor[:10]:  # Mostra primeiras 10
                    click.echo(
                        f"   Página {img['page']}: "
                        f"{img['width']}x{img['height']} ({img['ext']})"
                    )
                if len(extractor) > 10:
                    click.echo(f"   ... e mais {len(extractor) - 10} imagens")
                    
    except Exception as e:
        click.echo(f"Erro: {e}", err=True)


if __name__ == '__main__':
    cli()
