"""
Exemplo de uso do PDFForge.

Este script demonstra as principais funcionalidades da biblioteca.
"""

from pathlib import Path


def exemplo_basico():
    """Exemplo básico de uso do PDFForge."""
    from pdfforge import PDFDocument
    
    print("=" * 50)
    print("EXEMPLO BÁSICO - Carregar e extrair texto")
    print("=" * 50)
    
    # Nota: Este exemplo requer um arquivo PDF real
    # Substitua pelo caminho de um PDF no seu sistema
    pdf_path = Path("exemplo.pdf")
    
    if not pdf_path.exists():
        print(f"Arquivo {pdf_path} não encontrado.")
        print("Crie um arquivo de exemplo ou modifique o caminho.")
        return
    
    # Carregar documento
    with PDFDocument(pdf_path) as doc:
        print(f"\n📄 Arquivo: {doc.file_path.name}")
        print(f"📑 Páginas: {doc.page_count}")
        
        # Extrair texto
        texto = doc.extract_text()
        print(f"\n📝 Texto extraído ({len(texto)} caracteres):")
        print(texto[:500] + "..." if len(texto) > 500 else texto)


def exemplo_limpeza():
    """Exemplo de limpeza de texto."""
    from pdfforge import PDFDocument, DocumentCleaner
    
    print("\n" + "=" * 50)
    print("EXEMPLO - Limpeza de texto")
    print("=" * 50)
    
    pdf_path = Path("exemplo.pdf")
    
    if not pdf_path.exists():
        print(f"Arquivo {pdf_path} não encontrado.")
        return
    
    with PDFDocument(pdf_path) as doc:
        # Criar limpador
        cleaner = DocumentCleaner(doc)
        
        # Limpar com opções padrão
        texto_limpo = cleaner.clean()
        
        print(f"\n✨ Texto limpo ({len(texto_limpo)} caracteres)")
        
        # Extrair dados estruturados
        dados = cleaner.extract_structured_data()
        
        print(f"\n📊 Estatísticas:")
        print(f"   Palavras: {dados.get('word_count', 0)}")
        print(f"   Emails encontrados: {len(dados.get('emails', []))}")
        print(f"   URLs encontradas: {len(dados.get('urls', []))}")
        print(f"   Telefones encontrados: {len(dados.get('phones', []))}")


def exemplo_exportacao():
    """Exemplo de exportação para diferentes formatos."""
    from pdfforge import PDFDocument, ExportManager
    
    print("\n" + "=" * 50)
    print("EXEMPLO - Exportação para múltiplos formatos")
    print("=" * 50)
    
    pdf_path = Path("exemplo.pdf")
    
    if not pdf_path.exists():
        print(f"Arquivo {pdf_path} não encontrado.")
        return
    
    # Criar diretório de saída
    output_dir = Path("saida_exemplos")
    output_dir.mkdir(exist_ok=True)
    
    with PDFDocument(pdf_path) as doc:
        manager = ExportManager()
        
        # Exportar para Markdown
        md_file = output_dir / "documento.md"
        manager.export(doc, md_file, format="markdown")
        print(f"\n✅ Exportado para Markdown: {md_file}")
        
        # Exportar para JSON
        json_file = output_dir / "dados.json"
        manager.export(doc, json_file, format="json", pretty=True)
        print(f"✅ Exportado para JSON: {json_file}")
        
        # Exportar para HTML
        html_file = output_dir / "documento.html"
        manager.export(doc, html_file, format="html")
        print(f"✅ Exportado para HTML: {html_file}")
        
        # Exportar para TXT
        txt_file = output_dir / "documento.txt"
        manager.export(doc, txt_file, format="text")
        print(f"✅ Exportado para TXT: {txt_file}")


def exemplo_imagens():
    """Exemplo de extração de imagens."""
    from pdfforge import PDFDocument
    
    print("\n" + "=" * 50)
    print("EXEMPLO - Extração de imagens")
    print("=" * 50)
    
    pdf_path = Path("exemplo.pdf")
    
    if not pdf_path.exists():
        print(f"Arquivo {pdf_path} não encontrado.")
        return
    
    with PDFDocument(pdf_path) as doc:
        # Extrair informações das imagens
        imagens = doc.extract_images()
        
        print(f"\n📷 Imagens encontradas: {len(imagens)}")
        
        for i, img in enumerate(imagens[:5], 1):
            print(f"\n   Imagem {i}:")
            print(f"      Página: {img['page']}")
            print(f"      Tamanho: {img['width']}x{img['height']}")
            print(f"      Formato: {img['ext']}")
        
        if len(imagens) > 5:
            print(f"\n   ... e mais {len(imagens) - 5} imagens")
        
        # Salvar imagens
        if imagens:
            output_dir = Path("imagens_extraidas")
            output_dir.mkdir(exist_ok=True)
            
            extractor = doc.extract_images()
            salvas = extractor.save_images(output_dir)
            
            print(f"\n💾 {len(salvas)} imagens salvas em: {output_dir}")


def exemplo_lote():
    """Exemplo de processamento em lote."""
    from pdfforge import BatchProcessor
    
    print("\n" + "=" * 50)
    print("EXEMPLO - Processamento em lote")
    print("=" * 50)
    
    # Criar diretórios de exemplo
    input_dir = Path("pdfs_entrada")
    output_dir = Path("pdfs_saida")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Diretório de entrada: {input_dir}")
    print(f"📁 Diretório de saída: {output_dir}")
    
    # Verificar se há PDFs no diretório
    processor = BatchProcessor(
        input_dir=input_dir,
        output_dir=output_dir
    )
    
    pdfs = processor.find_pdfs()
    
    if not pdfs:
        print("\n⚠️  Nenhum PDF encontrado no diretório de entrada.")
        print(f"   Coloque arquivos PDF em: {input_dir.absolute()}")
        return
    
    print(f"\n📄 PDFs encontrados: {len(pdfs)}")
    
    # Processar em lote
    resultados = processor.process(
        pdf_files=pdfs,
        max_workers=2
    )
    
    sucesso = sum(1 for r in resultados if r.get('success'))
    print(f"\n✅ Processados {sucesso}/{len(resultados)} arquivos com sucesso")
    
    # Exportar todos para JSON
    exportados = processor.export_all(
        pdf_files=pdfs,
        format="json",
        output_dir=output_dir
    )
    
    print(f"💾 {len(exportados)} arquivos exportados para: {output_dir}")


def exemplo_info():
    """Exemplo de obtenção de informações do PDF."""
    from pdfforge import get_pdf_info, detect_pdf_type
    
    print("\n" + "=" * 50)
    print("EXEMPLO - Informações do PDF")
    print("=" * 50)
    
    pdf_path = Path("exemplo.pdf")
    
    if not pdf_path.exists():
        print(f"Arquivo {pdf_path} não encontrado.")
        return
    
    # Obter informações detalhadas
    info = get_pdf_info(pdf_path)
    
    print(f"\n📄 Arquivo: {info['file_name']}")
    print(f"📊 Tamanho: {info['file_size']:,} bytes")
    print(f"📑 Páginas: {info['page_count']}")
    print(f"📝 Tipo: {info['type']}")
    print(f"🔒 Criptografado: {'Sim' if info['is_encrypted'] else 'Não'}")
    
    # Detectar tipo
    tipo = detect_pdf_type(pdf_path)
    print(f"\n🎯 Tipo detectado: {tipo}")
    
    if tipo == "scanned":
        print("   ⚠️  Este PDF parece ser digitalizado.")
        print("   Use OCR para extrair texto.")
    elif tipo == "text":
        print("   ✅ PDF baseado em texto.")
    elif tipo == "mixed":
        print("   📊 PDF misto (texto e imagens).")


def main():
    """Executa todos os exemplos."""
    print("\n" + "=" * 60)
    print("  PDFForge - Exemplos de Uso")
    print("=" * 60)
    
    # Executar exemplos
    exemplo_info()
    exemplo_basico()
    exemplo_limpeza()
    exemplo_exportacao()
    exemplo_imagens()
    exemplo_lote()
    
    print("\n" + "=" * 60)
    print("  Exemplos concluídos!")
    print("=" * 60)
    print("\n📚 Para mais informações, consulte a documentação.")
    print("🌟 Contribua com o projeto: https://github.com/pdfforge\n")


if __name__ == "__main__":
    main()
