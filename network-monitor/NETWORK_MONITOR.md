# 🛡️ Network Monitor - Sistema de Monitoramento de Rede Doméstica

> **Ferramenta educacional e defensiva para monitorar SUA PRÓPRIA rede**  
> Detecte invasões, identifique dispositivos suspeitos e analise o tráfego de forma ética

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 📖 Visão Geral

Este projeto fornece um sistema completo de monitoramento de rede para usuários domésticos que suspeitam ter sido comprometidos. Inclui:

- **Opção A**: Script Python educacional com Scapy para captura e análise de pacotes
- **Opção B**: Solução profissional com Docker Compose (Pi-hole/AdGuard + Monitor)
- **Plano de Ação**: Guia passo-a-passo para responder a suspeitas de invasão

## ⚡ Quick Start

### Opção Rápida (Script Python)

```bash
# Clone ou navegue até o diretório
cd network-monitor

# Instale dependências
pip install -r python-scapy/requirements.txt

# Execute o monitor (5 minutos)
sudo python3 python-scapy/network_monitor.py

# Ou use o script interativo
./scripts/quickstart.sh
```

### Opção Completa (Docker)

```bash
cd docker-compose

# Criar diretórios necessários
mkdir -p pihole/etc-pihole logs/pihole logs/monitor captures

# Iniciar serviços
docker-compose up -d

# Acessar dashboard Pi-hole
# http://SEU_IP/admin (senha: ChangeMe123!)
```

## 📁 Estrutura do Projeto

```
network-monitor/
├── python-scapy/              # Opção A - Script Python
│   ├── network_monitor.py     # Script principal de captura
│   ├── Dockerfile             # Containerização do script
│   └── requirements.txt       # Dependências Python
│
├── docker-compose/            # Opção B - Solução Docker
│   ├── docker-compose.yml     # Orquestração de serviços
│   └── ADGUARD_CONFIG.md      # Configuração AdGuard Home
│
├── scripts/                   # Scripts utilitários
│   └── quickstart.sh          # Menu interativo
│
├── docs/                      # Documentação completa
│   ├── README.md              # Guia principal
│   └── ANALISE_EXEMPLOS.md    # Exemplos de análise
│
└── NETWORK_MONITOR.md         # Este arquivo
```

## 🎯 Funcionalidades

### Captura de Metadados
- ✅ IPs de origem e destino
- ✅ Portas e protocolos
- ✅ Consultas DNS (domínios acessados)
- ✅ Endereços MAC (identificação de fabricantes)
- ✅ Volume de tráfego por conexão

### Detecção de Anomalias
- ⚠️ Conexões para portas suspeitas (4444, 6666, 31337, etc.)
- ⚠️ Tráfego em volume anormal
- ⚠️ Domínios potencialmente maliciosos
- ⚠️ Dispositivos desconhecidos na rede

### Análise Forense
- 📊 Logs estruturados em JSON
- 📊 Capturas PCAP para Wireshark
- 📊 Estatísticas agregadas
- 📊 Mapeamento IP-MAC

## 🔒 O Que Este Sistema Faz vs. Não Faz

| Faz ✅ | Não Faz ❌ |
|--------|-----------|
| Captura metadados (envelope) | Lê conteúdo criptografado |
| Identifica domínios DNS | Quebra HTTPS/TLS |
| Detecta portas suspeitas | É ferramenta ofensiva |
| Mapeia dispositivos | Monitora redes de terceiros |
| Gera alertas de anomalia | Substitui antivírus/firewall |

## 🚨 Suspeita de Invasão?

Siga o **Plano de Ação** documentado em [README.md](docs/README.md):

1. **Mapeie dispositivos** conectados
2. **Verifique portas abertas** no roteador
3. **Segregue a rede** (VLANs, rede de convidados)
4. **Rotacione credenciais** (Wi-Fi, admin, contas)
5. **Analise forense local** (extensões, startup, tarefas)
6. **Revise logs** do monitor

## 📚 Documentação Completa

- **[Guia Principal](docs/README.md)**: Instruções detalhadas de instalação, uso e troubleshooting
- **[Análise de Logs](docs/ANALISE_EXEMPLOS.md)**: Scripts e exemplos para interpretar dados capturados
- **[AdGuard Home](docker-compose/ADGUARD_CONFIG.md)**: Configuração alternativa ao Pi-hole

## 🛠️ Requisitos

### Mínimos
- Python 3.8+
- Linux, macOS ou Windows (WSL)
- Permissões de root/sudo para captura de pacotes

### Recomendados
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM livre
- Espaço em disco: 1GB+

## 💡 Exemplos de Uso

### Monitoramento Básico
```bash
# Executar por 5 minutos
sudo python3 python-scapy/network_monitor.py -t 300
```

### Escanear Rede
```bash
# Descobrir todos os dispositivos
sudo python3 python-scapy/network_monitor.py --scan
```

### Apenas DNS
```bash
# Monitorar apenas consultas DNS
sudo python3 python-scapy/network_monitor.py --dns-only -t 600
```

### Docker Completo
```bash
# Iniciar stack completa
cd docker-compose
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f
```

## 🔧 Troubleshooting

| Problema | Solução |
|----------|---------|
| Permission denied | Execute com `sudo` ou adicione capacidades Docker |
| No interface found | Especifique interface com `-i eth0` |
| Pi-hole não responde | Verifique firewall (porta 53, 80) |
| Muitos falsos positivos | Ajuste thresholds no código |

Consulte [README.md](docs/README.md#troubleshooting) para mais detalhes.

## 📈 Próximos Passos

Após implementar:

1. **Monitore continuamente** (deixe rodando 24h+)
2. **Estabeleça baseline** do tráfego normal
3. **Configure alertas** automáticos
4. **Integre com SIEM** (opcional, ELK/Splunk)
5. **Compartilhe feedback** para melhorar o projeto

## ⚖️ Aviso Legal

**ESTE SOFTWARE É PARA FINS EDUCACIONAIS E DEFENSIVOS.**

- Use APENAS em redes que você possui ou tem autorização explícita
- Monitorar redes de terceiros sem consentimento é ILEGAL
- Respeite leis de privacidade (LGPD, GDPR)
- Os autores não se responsabilizam por mau uso

## 🤝 Contribuição

Contribuições são bem-vindas!

- 🐛 Report bugs via GitHub Issues
- 💡 Sugira melhorias
- 🔧 Envie Pull Requests
- 📖 Melhore a documentação

## 📞 Recursos Adicionais

- **CERT.br**: Centro de Estudos de Incidentes de Segurança (Brasil)
- **Polícia Federal**: Divisão de Crimes Cibernéticos
- **AbuseIPDB**: Reportar IPs maliciosos
- **Have I Been Pwned**: Verificar vazamentos de dados

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**Versão**: 1.0.0  
**Última atualização**: Janeiro 2024  
**Status**: Estável para uso educacional

> "A segurança começa com o conhecimento do que está acontecendo na sua rede."
