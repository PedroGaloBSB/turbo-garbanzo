# Política de Privacidade e Conformidade LGPD

## PDFForge - Lei Geral de Proteção de Dados (Lei nº 13.709/2018)

### 1. Controlador de Dados
**PDFForge** - Ferramenta Opensource de Manipulação de PDFs  
Responsável: Comunidade PDFForge  
Contato: privacy@pdfforge.org (fictício)

### 2. Dados Coletados

#### 2.1 Usuários Anônimos (sem login)
- **Arquivos PDF**: Armazenados temporariamente (máximo 24 horas)
- **Hash do arquivo**: Para identificação única
- **IP anonimizado**: Último octeto removido (ex: 192.168.1.XXX)
- **Logs de processamento**: Tipo de operação, timestamp, formatos solicitados

#### 2.2 Usuários Autenticados (Google Login)
- **ID do Google**: Identificador único
- **Email**: Para comunicação e recuperação
- **Nome**: Personalização da experiência
- **Histórico de processamentos**: Metadados das operações
- **Preferências**: Configurações salvas

### 3. Finalidades do Tratamento

| Finalidade | Base Legal | Dados Envolvidos |
|------------|-----------|------------------|
| Processamento de PDFs | Execução de contrato | Arquivo, hash, IP |
| Melhoria do serviço | Interesse legítimo | Logs anonimizados |
| Suporte ao usuário | Consentimento | Email, histórico |
| Conformidade legal | Obrigação legal | Todos (quando requisitado) |

### 4. Direitos dos Titulares (Art. 18)

Você tem direito a:
- ✅ **Confirmação** da existência de tratamento
- ✅ **Acesso** aos seus dados
- ✅ **Correção** de dados incompletos/exatos
- ✅ **Anonimização/bloqueio/eliminação** de dados
- ✅ **Portabilidade** dos dados (exportação em JSON/CSV)
- ✅ **Eliminação** de dados tratados com consentimento
- ✅ **Informação** sobre compartilhamento
- ✅ **Revogação** do consentimento a qualquer tempo

### 5. Como Exercer Seus Direitos

#### 5.1 Acesso aos Dados
```bash
# Via API
curl -X GET "http://api.pdfforge.org/api/lgpd/access" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 5.2 Eliminação de Dados
```bash
# Eliminação imediata
curl -X POST "http://api.pdfforge.org/api/lgpd/delete?immediate=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 5.3 Portabilidade
```bash
# Exportar dados em JSON
curl -X GET "http://api.pdfforge.org/api/lgpd/portability?format=json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Tempo de Retenção

| Categoria de Dado | Período de Retenção |
|-------------------|---------------------|
| Arquivos de usuários anônimos | Até download ou 24h |
| Arquivos de usuários logados | Até exclusão manual |
| Logs de processamento | 30 dias |
| Metadados de usuários | 1 ano após última atividade |
| Dados de consentimento | Enquanto ativo + 5 anos |

### 7. Medidas de Segurança

- 🔒 **Criptografia**: TLS 1.3 em trânsito, AES-256 em repouso
- 🔐 **Autenticação**: OAuth 2.0 Google, JWT tokens
- 🛡️ **Sanitização**: Remoção de scripts maliciosos de PDFs
- 📝 **Logging**: Registro de todas as operações de tratamento
- 🗑️ **Eliminação automática**: Cleanup agendado de dados temporários
- ⚡ **Rate limiting**: Proteção contra abuso (10 req/min)

### 8. Compartilhamento de Dados

**NÃO compartilhamos** dados pessoais com terceiros, exceto:
- Quando exigido por ordem judicial
- Para prestadores de serviço essenciais (Google OAuth, hospedagem)
- Dados anonimizados para estatísticas de uso

### 9. Transferência Internacional

O PDFForge é um projeto global. Dados podem ser processados em servidores distribuídos mundialmente, sempre com proteções equivalentes à LGPD.

### 10. Atualizações desta Política

Esta política pode ser atualizada periodicamente. Alterações significativas serão comunicadas aos usuários.

**Última atualização**: Junho 2024

### 11. Relatório de Impacto (DPIA)

Um Relatório de Impacto à Proteção de Dados está disponível mediante solicitação via API:

```bash
curl -X GET "http://api.pdfforge.org/api/lgpd/dpia" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 12. Encarregado de Dados (DPO)

Para questões sobre privacidade e proteção de dados:
- Email: dpo@pdfforge.org (fictício)
- Formulário: https://pdfforge.org/privacy-contact

---

*Este documento está em conformidade com a Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018*
