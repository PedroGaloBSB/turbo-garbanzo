# 🛡️ Network Monitor - Guia Completo de Segurança Doméstica

> **AVISO IMPORTANTE**: Este sistema é apenas para monitoramento DEFENSIVO da SUA PRÓPRIA rede.  
> O uso em redes de terceiros sem autorização é ILEGAL e antiético.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Opção A - Script Python com Scapy](#opção-a---script-python-com-scapy)
3. [Opção B - Solução Profissional com Docker Compose](#opção-b---solução-profissional-com-docker-compose)
4. [Plano de Ação para Suspeita de Invasão](#plano-de-ação-para-suspeita-de-invasão)
5. [Troubleshooting](#troubleshooting)
6. [Próximos Passos](#próximos-passos)

---

## 🎯 Visão Geral

### O Que Este Sistema Faz

Este monitorador de rede foi projetado para ajudar usuários domésticos a:

- ✅ **Identificar dispositivos conectados** à sua rede (incluindo intrusos)
- ✅ **Monitorar consultas DNS** (quais domínios estão sendo acessados)
- ✅ **Detectar conexões suspeitas** (portas incomuns, tráfego anômalo)
- ✅ **Capturar metadados** de pacotes (IPs, portas, protocolos, volumes)
- ✅ **Gerar logs persistentes** para análise forense posterior

### O Que Este Sistema NÃO Faz

- ❌ **Não quebra criptografia** HTTPS/TLS (nem tenta)
- ❌ **Não lê conteúdo** de comunicações criptografadas
- ❌ **Não intercepta senhas** ou dados sensíveis
- ❌ **Não é uma ferramenta ofensiva** de hacking

### Por Que Esta Arquitetura?

| Componente | Função | Por Que Usar |
|------------|--------|--------------|
| **Scapy (Python)** | Captura flexível de pacotes | Altamente customizável, educacional |
| **Pi-hole** | DNS sinkhole + dashboard | Interface web amigável, blocking automático |
| **Docker** | Containerização | Isolamento, fácil deploy, portabilidade |
| **Grafana** | Visualização (opcional) | Dashboards profissionais |

---

## 🐍 Opção A - Script Python com Scapy

### Instalação

#### 1. Instalar Dependências do Sistema

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y python3-pip libpcap-dev tcpdump

# Fedora/RHEL
sudo dnf install -y python3-pip libpcap-devel tcpdump

# Arch Linux
sudo pacman -S python-pip libpcap tcpdump
```

#### 2. Instalar Dependências Python

```bash
cd /workspace/network-monitor/python-scapy
pip install -r requirements.txt
```

### Uso Básico

```bash
# Executar monitoramento por 5 minutos (300 segundos)
sudo python network_monitor.py

# Especificar interface de rede
sudo python network_monitor.py -i eth0

# Monitorar apenas tráfego DNS
sudo python network_monitor.py --dns-only -t 600

# Modo silencioso (menos output)
sudo python network_monitor.py -q -t 300

# Escanear rede em busca de dispositivos
sudo python network_monitor.py --scan
```

### Opções de Linha de Comando

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `-i, --interface` | Interface de rede | Auto-detect |
| `-t, --timeout` | Tempo em segundos | 300 |
| `-c, --count` | Número de pacotes | Ilimitado |
| `-l, --log-file` | Arquivo de log | network_traffic.log |
| `--dns-only` | Apenas DNS | False |
| `-q, --quiet` | Reduzir verbosidade | False |
| `--scan` | Modo scanner ARP | False |

### Estrutura do Código (Educacional)

O script é dividido em componentes claros:

```
network_monitor.py
├── MonitorConfig          # Configurações do monitor
├── PacketMetadata         # Estrutura de dados para metadados
├── TrafficSummary         # Estatísticas agregadas
├── NetworkMonitor         # Classe principal de captura
│   ├── extract_packet_metadata()  # Extrai info do pacote
│   ├── extract_dns_query()        # Captura consultas DNS
│   ├── log_suspicious_activity()  # Detecta anomalias
│   └── start_capture()            # Inicia captura
└── ARPScanner             # Descoberta de dispositivos
    └── scan_network()     # Varre a rede local
```

### Exemplo de Saída

```
╔══════════════════════════════════════════════════════════╗
║           NETWORK MONITOR - EDUCATIONAL TOOL             ║
║                                                          ║
║  For defensive monitoring of YOUR OWN network only      ║
║  Respects privacy - captures metadata only              ║
╚══════════════════════════════════════════════════════════╝

Available interfaces: ['lo', 'eth0', 'wlan0']

============================================================
Starting Network Monitor
============================================================
Using interface: eth0
Capture timeout: 300s
Packet count limit: unlimited
============================================================

2024-01-15 10:30:45 - INFO - TCP | 192.168.1.100:54321 -> 8.8.8.8:443 | 128 bytes
2024-01-15 10:30:46 - INFO - DNS Query: google.com
2024-01-15 10:30:47 - WARNING - SUSPICIOUS: Connection to suspicious port 4444 | 192.168.1.100 -> 203.0.113.50:4444

--- CAPTURE STATISTICS ---
Total Packets: 15234
Total Bytes: 2,456,789
Unique IPs: 45
DNS Queries Captured: 234
Suspicious Events: 3
```

### Build com Docker

```bash
# Construir imagem Docker
cd /workspace/network-monitor/python-scapy
docker build -t network-monitor:latest .

# Executar container
docker run --rm \
  --network host \
  --cap-add=NET_RAW \
  --cap-add=NET_ADMIN \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/captures:/app/captures \
  network-monitor:latest
```

---

## 🐳 Opção B - Solução Profissional com Docker Compose

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Permissões de root/sudo

### Instalação Rápida

```bash
cd /workspace/network-monitor/docker-compose

# Criar diretórios necessários
mkdir -p pihole/etc-pihole pihole/etc-dnsmasq.d logs/pihole logs/monitor captures grafana/data

# Iniciar serviços
docker-compose up -d
```

### Configuração do Pi-hole

1. **Acessar Dashboard Web**
   ```
   http://SEU_IP:80/admin
   Senha: ChangeMe123! (MUDE ISSO!)
   ```

2. **Configurar como DNS da Rede**
   
   No seu roteador, configure o servidor DNS para apontar para o IP da máquina rodando Pi-hole.
   
   Ou manualmente em cada dispositivo:
   ```
   DNS Primário: IP_DA_MAQUINA
   DNS Secundário: 1.1.1.1 (backup)
   ```

3. **Ativar Listas de Bloqueio**
   - Acesse: Admin → Group Management → Adlists
   - Adicione listas de domínios maliciosos:
     ```
     https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
     https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt
     ```

### Acessando Logs e Métricas

#### Pi-hole Dashboard
- **URL**: `http://SEU_IP/admin`
- **Funcionalidades**:
  - Total de queries DNS
  - Domínios bloqueados
  - Dispositivos mais ativos
  - Tipos de queries
  - Histórico completo

#### Logs do Network Monitor
```bash
# Ver logs em tempo real
tail -f logs/monitor/network_traffic.log

# Analisar JSON summary
cat logs/monitor/network_traffic.json | jq '.'

# Ver capturas PCAP
tcpdump -r captures/capture.pcap -n
```

#### Grafana (Opcional)
```bash
# Iniciar com perfil de monitoramento
docker-compose --profile monitoring up -d

# Acessar dashboard
http://SEU_IP:3000
Login: admin / ChangeMe123!
```

### Comandos Úteis

```bash
# Ver status dos serviços
docker-compose ps

# Ver logs
docker-compose logs -f pihole
docker-compose logs -f network-monitor

# Reiniciar serviço
docker-compose restart pihole

# Parar tudo
docker-compose down

# Atualizar imagens
docker-compose pull
docker-compose up -d
```

---

## 🚨 Plano de Ação para Suspeita de Invasão

Se você suspeita que foi hackeado, siga estes passos **IMEDIATAMENTE**:

### Passo 1: Mapeamento de Dispositivos Conectados

```bash
# Usar o scanner ARP incluído
sudo python network_monitor.py --scan

# Alternativa com nmap
sudo nmap -sn 192.168.1.0/24

# Ver tabela ARP do sistema
arp -a

# Comparar MAC addresses encontrados com seus dispositivos conhecidos
cat network_devices.json | jq '.devices[]'
```

**O que procurar:**
- Dispositivos que você não reconhece
- Múltiplos dispositivos com mesmo nome
- Fabricantes incomuns (ex: "Unknown" pode ser dispositivo falsificado)

### Passo 2: Verificação de Portas Abertas no Roteador

1. **Acessar Admin do Roteador**
   ```
   URL: http://192.168.1.1 ou http://192.168.0.1
   (verifique no rótulo do roteador)
   ```

2. **Verificar Port Forwarding**
   - Navegue até: Advanced → NAT Forwarding → Virtual Servers
   - Procure regras suspeitas encaminhando portas para IPs internos
   - Regras legítimas: jogos, servidores específicos que VOCÊ configurou
   - Regras suspeitas: portas aleatórias, IPs desconhecidos

3. **Verificar UPnP**
   - UPnP pode abrir portas automaticamente
   - Desative se não estiver usando
   - Revogue permissões antigas

### Passo 3: Segregação de Rede

```bash
# Se seu roteador suporta VLANs:
# 1. Crie VLAN separada para IoT
# 2. Isole dispositivos convidados
# 3. Mantenha computadores principais em VLAN segura

# Configurar rede de convidados no roteador:
# - Ativar "Guest Network"
# - Habilitar "AP Isolation"
# - Limitar acesso à rede principal
```

**Por que isso importa:**
- Dispositivos IoT são frequentemente vulneráveis
- Se um dispositivo IoT é comprometido, não pode acessar seus PCs
- Visitantes não podem escanear sua rede interna

### Passo 4: Rotação de Credenciais

**IMEDIATAMENTE:**

1. **Wi-Fi**
   ```
   - Mudar senha WPA2/WPA3
   - Usar senha forte: 20+ caracteres, misturar tipos
   - Desativar WPS (vulnerável)
   ```

2. **Admin do Roteador**
   ```
   - Mudar senha de administrador
   - Desativar acesso remoto (WAN)
   - Atualizar firmware do roteador
   ```

3. **Contas Online**
   ```
   - Email principal
   - Contas bancárias
   - Redes sociais
   - Ativar 2FA em TUDO
   ```

4. **Computadores Locais**
   ```
   - Mudar senhas de usuário
   - Verificar chaves SSH conhecidas (~/.ssh/authorized_keys)
   - Resetar credenciais salvas no navegador
   ```

### Passo 5: Análise Forense Local

#### Extensões de Navegador
```bash
# Chrome/Chromium
ls ~/.config/google-chrome/Default/Extensions/

# Firefox
ls ~/.mozilla/firefox/*/extensions/

# Verificar extensões suspeitas:
# - Não reconhecidas
# - Sem nome/descrição
# - Pedem permissões excessivas
```

#### Programas de Inicialização

**Linux:**
```bash
# Systemd services
systemctl list-unit-files --type=service --state=enabled

# User autostart
ls ~/.config/autostart/
cat /etc/rc.local

# Cron jobs
crontab -l
sudo cat /etc/crontab
ls /etc/cron.d/
```

**Windows:**
```powershell
# Task Manager → Startup
# Ou PowerShell:
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command
```

#### Tarefas Agendadas Suspeitas

**Linux:**
```bash
# Ver todas as tarefas cron
sudo grep -r "" /etc/cron.*

# Ver logs de execução
sudo grep CRON /var/log/syslog
```

**Windows:**
```powershell
Get-ScheduledTask | Where-Object {$_.State -eq 'Ready'}
```

#### Conexões de Rede Ativas

```bash
# Linux/Mac
sudo netstat -tulpn
sudo ss -tulpn
sudo lsof -i -P -n

# Windows
netstat -ano
```

**Procure por:**
- Conexões para IPs estrangeiros desconhecidos
- Portas incomuns (4444, 5555, 6666, 31337)
- Processos desconhecidos fazendo conexões

### Passo 6: Análise de Logs do Monitor

```bash
# Identificar domínios mais acessados
cat logs/monitor/network_traffic.json | \
  jq -r '.dns_queries[]' | sort | uniq -c | sort -rn | head -20

# Procurar eventos suspeitos
cat logs/monitor/network_traffic.json | \
  jq '.suspicious_events[]'

# Ver conexões mais frequentes
cat logs/monitor/network_traffic.json | \
  jq -r '.top_connections[] | "\(.[0]): \(.[1])"'
```

**Red Flags:**
- Domínios de mineração de criptomoedas
- Serviços de Dynamic DNS estranhos (no-ip, dyndns)
- Conexões para países sob sanções (dependendo do seu uso)
- Tráfego em horários incomuns (madrugada)

---

## 🔧 Troubleshooting

### Problema: "Permission Denied" ao Capturar Pacotes

**Solução:**
```bash
# Executar como root
sudo python network_monitor.py

# OU dar permissão ao Python (menos seguro)
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3

# Em Docker, verificar capacidades
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN ...
```

### Problema: "No Interface Found"

**Solução:**
```bash
# Listar interfaces disponíveis
ip link show

# Especificar interface manualmente
sudo python network_monitor.py -i eth0

# Verificar se interface está UP
sudo ip link set eth0 up
```

### Problema: Pi-hole Não Recebe Queries DNS

**Solução:**
1. Verificar se firewall permite porta 53:
   ```bash
   sudo ufw allow 53/tcp
   sudo ufw allow 53/udp
   ```

2. Confirmar que dispositivos usam Pi-hole como DNS:
   ```bash
   nslookup google.com
   # Deve mostrar IP do Pi-hole como servidor
   ```

3. Verificar logs do dnsmasq:
   ```bash
   docker-compose logs pihole | grep dnsmasq
   ```

### Problema: Muitas Mensagens de Log (Ruído)

**Solução:**
```bash
# Usar modo quiet
sudo python network_monitor.py -q

# Filtrar apenas DNS
sudo python network_monitor.py --dns-only

# Aplicar filtro BPF personalizado
# Editar network_monitor.py e modificar bpf_filter
```

### Problema: Container Docker Não Inicia

**Solução:**
```bash
# Ver logs do container
docker-compose logs network-monitor

# Verificar se porta já está em uso
sudo netstat -tulpn | grep :80

# Testar build manualmente
docker build -t network-monitor:test ./python-scapy
docker run --rm -it network-monitor:test bash
```

---

## 📈 Próximos Passos

### Melhorias Imediatas

1. **Configurar Alertas Automáticos**
   ```bash
   # Script para monitorar logs e enviar alertas
   # Exemplo: email, Telegram, Discord webhook
   ```

2. **Integrar com SIEM**
   - Elastic Stack (ELK)
   - Splunk (versão free)
   - Graylog

3. **Automatizar Respostas**
   - Bloquear IPs suspeitos automaticamente
   - Desconectar dispositivos não autorizados
   - Notificar em tempo real

### Aprendizado Contínuo

**Recursos Recomendados:**

- 📚 Livros:
  - "Network Security Through Data Analysis" - Michael Collins
  - "Practical Packet Analysis" - Chris Sanders

- 🎓 Cursos:
  - Coursera: Network Security Specialization
  - SANS SEC503: Network Monitoring and Threat Detection

- 🛠️ Ferramentas para Explorar:
  - Wireshark (análise forense de pacotes)
  - Zeek/Bro (IDS de rede)
  - Suricata (IPS/IDS)
  - Security Onion (distro completa de monitoramento)

### Quando Buscar Ajuda Profissional

Considere contratar um especialista em segurança se:

- ✅ Encontrar malware confirmado em múltiplos dispositivos
- ✅ Dados financeiros foram comprometidos
- ✅ Identidade roubada ou fraude ocorrendo
- ✅ Ameaças diretas ou extortion
- ✅ Não consegue remover a invasão sozinho

**No Brasil:**
- Polícia Federal - Divisão de Crimes Cibernéticos
- CERT.br - Centro de Estudos, Resposta e Tratamento de Incidentes de Segurança

---

## 📞 Suporte e Contribuição

Este é um projeto educacional open-source. Contribuições são bem-vindas!

**Reportar Bugs:** Abra uma issue no repositório  
**Sugerir Melhorias:** Pull requests são apreciados  
**Dúvidas:** Consulte a documentação ou fóruns especializados

---

## ⚖️ Aviso Legal

ESTE SOFTWARE É FORNECIDO "COMO ESTÁ" PARA FINS EDUCACIONAIS E DE DEFESA PESSOAL.

- Use APENAS em redes que você possui ou tem autorização explícita para monitorar
- O monitoramento de redes de terceiros sem consentimento é ILEGAL
- Os autores não se responsabilizam por mau uso desta ferramenta
- Respeite leis de privacidade locais (LGPD no Brasil, GDPR na Europa)

---

**Última Atualização:** Janeiro 2024  
**Versão:** 1.0.0
