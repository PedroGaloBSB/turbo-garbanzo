# 📊 Exemplo de Análise de Logs

Este documento mostra como analisar os dados capturados pelo monitor de rede.

## Estrutura do JSON de Saída

O arquivo `network_traffic.json` contém:

```json
{
  "capture_end_time": "2024-01-15T10:35:45.123456",
  "total_packets": 15234,
  "total_bytes": 2456789,
  "unique_ips": ["192.168.1.1", "192.168.1.100", "8.8.8.8", ...],
  "dns_queries": [
    "google.com",
    "facebook.com",
    "api.whatsapp.com",
    ...
  ],
  "top_connections": [
    ["192.168.1.100:8.8.8.8", 1234],
    ["192.168.1.100:142.250.78.14", 567],
    ...
  ],
  "suspicious_events": [
    {
      "timestamp": "2024-01-15T10:32:15.123456",
      "type": "SUSPICIOUS_ACTIVITY",
      "description": "Connection to suspicious port 4444",
      "src_ip": "192.168.1.100",
      "dst_ip": "203.0.113.50",
      "port": 4444
    }
  ],
  "ip_mac_mapping": {
    "192.168.1.100": "aa:bb:cc:dd:ee:ff",
    "192.168.1.1": "00:11:22:33:44:55"
  }
}
```

## Scripts de Análise

### 1. Top Domínios Acessados

```python
#!/usr/bin/env python3
"""Analisar domínios DNS mais frequentes."""

import json
from collections import Counter
from pathlib import Path

def analyze_dns(log_file="logs/monitor/network_traffic.json"):
    with open(log_file) as f:
        data = json.load(f)
    
    queries = data.get('dns_queries', [])
    counts = Counter(queries)
    
    print("=" * 60)
    print("TOP 20 DOMÍNIOS ACESSADOS")
    print("=" * 60)
    
    for domain, count in counts.most_common(20):
        print(f"{count:5d}x - {domain}")
    
    return counts

if __name__ == '__main__':
    analyze_dns()
```

### 2. Detectar Comportamentos Anômalos

```python
#!/usr/bin/env python3
"""Detectar padrões suspeitos no tráfego."""

import json
from datetime import datetime

SUSPICIOUS_KEYWORDS = [
    'mining', 'pool', 'crypto',
    'hack', 'exploit', 'malware',
    'no-ip', 'dyndns', 'afraid',  # Dynamic DNS services
    'torrent', 'p2p',
]

PORTS_OF_INTEREST = {
    4444: 'Metasploit/RAT',
    5555: 'Android Debug',
    6666: 'IRC (Malware C&C)',
    6667: 'IRC',
    31337: 'Back Orifice',
    23: 'Telnet (Insecure)',
    3389: 'RDP',
    445: 'SMB (WannaCry)',
    1433: 'MSSQL',
    3306: 'MySQL',
}

def analyze_anomalies(log_file="logs/monitor/network_traffic.json"):
    with open(log_file) as f:
        data = json.load(f)
    
    print("=" * 60)
    print("ANÁLISE DE ANOMALIAS")
    print("=" * 60)
    
    # 1. Eventos já marcados como suspeitos
    events = data.get('suspicious_events', [])
    if events:
        print(f"\n⚠️  EVENTOS SUSPEITOS DETECTADOS: {len(events)}\n")
        for event in events:
            print(f"  [{event['timestamp']}]")
            print(f"  {event['description']}")
            print(f"  {event['src_ip']} → {event['dst_ip']}:{event.get('port', 'N/A')}")
            print()
    
    # 2. Procurar domínios suspeitos
    dns_queries = data.get('dns_queries', [])
    suspicious_domains = []
    
    for query in dns_queries:
        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword.lower() in query.lower():
                suspicious_domains.append((query, keyword))
                break
    
    if suspicious_domains:
        print(f"\n⚠️  DOMÍNIOS POTENCIALMENTE SUSPEITOS: {len(suspicious_domains)}\n")
        for domain, reason in set(suspicious_domains):
            print(f"  • {domain} (keyword: {reason})")
    
    # 3. Conexões para portas interessantes
    connections = data.get('top_connections', [])
    suspicious_conns = []
    
    for conn_str, count in connections:
        try:
            # Parse connection string
            parts = conn_str.split(':')
            if len(parts) >= 4:
                dst_port = int(parts[-1])
                if dst_port in PORTS_OF_INTEREST:
                    suspicious_conns.append((conn_str, count, PORTS_OF_INTEREST[dst_port]))
        except (ValueError, IndexError):
            continue
    
    if suspicious_conns:
        print(f"\n⚠️  CONEXÕES EM PORTAS INTERESSANTES:\n")
        for conn, count, service in suspicious_conns:
            print(f"  {count:5d}x - {conn} ({service})")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    analyze_anomalies()
```

### 3. Mapeamento de Dispositivos

```python
#!/usr/bin/env python3
"""Identificar dispositivos na rede por MAC Address."""

import json
from collections import defaultdict

# Vendors conhecidos
VENDORS = {
    '00:50:56': 'VMware',
    '08:00:27': 'VirtualBox',
    'B8:27:EB': 'Raspberry Pi',
    'DC:A6:32': 'Intel',
    '00:1A:2B': 'Apple',
    '3C:5A:B4': 'Google',
    'F0:B4:79': 'Amazon',
    '5C:50:15': 'Samsung',
    '04:DA:D2': 'Xiaomi',
}

def identify_vendor(mac):
    oui = mac[:8].upper()
    return VENDORS.get(oui, 'Unknown')

def map_devices(log_file="logs/monitor/network_traffic.json"):
    with open(log_file) as f:
        data = json.load(f)
    
    ip_mac_map = data.get('ip_mac_mapping', {})
    
    print("=" * 60)
    print("MAPEAMENTO DE DISPOSITIVOS")
    print("=" * 60)
    print(f"\n{'IP':<18} {'MAC Address':<18} {'Vendor'}")
    print("-" * 60)
    
    devices_by_vendor = defaultdict(list)
    
    for ip, mac in sorted(ip_mac_map.items()):
        vendor = identify_vendor(mac)
        print(f"{ip:<18} {mac:<18} {vendor}")
        devices_by_vendor[vendor].append(ip)
    
    print("\n" + "=" * 60)
    print("RESUMO POR FABRICANTE")
    print("=" * 60)
    
    for vendor, ips in sorted(devices_by_vendor.items(), 
                               key=lambda x: len(x[1]), 
                               reverse=True):
        print(f"{vendor}: {len(ips)} dispositivo(s)")
    
    # Identificar IPs locais vs externos
    local_ips = [ip for ip in ip_mac_map.keys() 
                 if ip.startswith('192.168.') or 
                    ip.startswith('10.') or 
                    ip.startswith('172.')]
    
    external_ips = set(ip_mac_map.keys()) - set(local_ips)
    
    print(f"\nDispositivos locais: {len(local_ips)}")
    print(f"IPs externos contatados: {len(external_ips)}")
    
    if external_ips:
        print("\nIPs externos mais acessados:")
        for ip in list(external_ips)[:10]:
            print(f"  • {ip}")

if __name__ == '__main__':
    map_devices()
```

### 4. Linha do Tempo de Atividade

```python
#!/usr/bin/env python3
"""Visualizar atividade de rede por hora."""

import json
from collections import defaultdict
from datetime import datetime

def timeline_analysis(log_file="logs/monitor/network_traffic.json"):
    with open(log_file) as f:
        data = json.load(f)
    
    # Agrupar eventos por hora
    hourly_activity = defaultdict(int)
    
    # Usar timestamp do capture_end_time como referência
    end_time = datetime.fromisoformat(data['capture_end_time'])
    
    # Estimar distribuição baseada no total de packets
    # (Em produção, use timestamps reais de cada packet)
    total_packets = data['total_packets']
    
    print("=" * 60)
    print("ESTATÍSTICAS DA CAPTURA")
    print("=" * 60)
    
    print(f"\nPeríodo: Até {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de pacotes: {total_packets:,}")
    print(f"Total de bytes: {data['total_bytes']:,}")
    print(f"Duração estimada: {data.get('capture_duration', 'N/A')}")
    
    # Volume por tipo de protocolo (se disponível)
    print("\n" + "=" * 60)
    print("RECOMENDAÇÕES")
    print("=" * 60)
    
    dns_count = len(data.get('dns_queries', []))
    suspicious_count = len(data.get('suspicious_events', []))
    
    if suspicious_count > 0:
        print(f"\n⚠️  {suspicious_count} evento(s) suspeito(s) detectado(s)!")
        print("   Revise a seção de suspicious_events no JSON.")
    
    if dns_count > 1000:
        print(f"\nℹ️  Alto volume de consultas DNS: {dns_count}")
        print("   Considere usar Pi-hole/AdGuard para filtragem.")
    
    unique_ips = len(data.get('unique_ips', []))
    if unique_ips > 50:
        print(f"\nℹ️  Muitos IPs únicos: {unique_ips}")
        print("   Verifique se todos os dispositivos são conhecidos.")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    timeline_analysis()
```

## Queries SQL (se importar para banco)

Se você importar os dados para SQLite ou outro banco:

```sql
-- Top domínios acessados
SELECT domain, COUNT(*) as count 
FROM dns_queries 
GROUP BY domain 
ORDER BY count DESC 
LIMIT 20;

-- Conexões por IP de destino
SELECT dst_ip, COUNT(*) as connections, SUM(packet_size) as total_bytes
FROM packets
GROUP BY dst_ip
ORDER BY connections DESC
LIMIT 20;

-- Detecção de portas suspeitas
SELECT * FROM packets
WHERE dst_port IN (4444, 5555, 6666, 6667, 31337, 23, 3389);

-- Atividade por hora
SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour, COUNT(*) as packets
FROM packets
GROUP BY hour
ORDER BY hour;
```

## Integração com Ferramentas Externas

### Wireshark

```bash
# Abrir captura no Wireshark
wireshark captures/capture.pcap

# Filtrar tráfego suspeito no Wireshark
tcp.port == 4444
dns.qry.name contains "mining"
ip.dst == 203.0.113.0/24
```

### Zeek/Bro

Para análise mais avançada, integre com Zeek:

```bash
# Processar PCAP com Zeek
zeek -r captures/capture.pcap

# Analisar logs gerados
cat conn.log | cut -f2,3,4 | sort | uniq -c
```

### Elastic Stack (ELK)

Para visualização profissional:

1. **Instalar Elastic Stack**
2. **Configurar Filebeat** para ler logs JSON
3. **Criar dashboards no Kibana**

Exemplo de pipeline Logstash:

```ruby
input {
  file {
    path => "/path/to/network_traffic.json"
    codec => json
  }
}

filter {
  geoip {
    source => "dst_ip"
    target => "geo"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "network-monitor-%{+YYYY.MM.dd}"
  }
}
```

---

## Próximos Passos

1. Execute o monitor por um período representativo (24h+)
2. Analise os resultados com os scripts acima
3. Identifique padrões anômalos
4. Tome ações corretivas se necessário
5. Automatize a análise contínua
