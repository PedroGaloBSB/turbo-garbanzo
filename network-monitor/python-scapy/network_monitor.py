#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Monitor - Educational Packet Capture Tool
==================================================

This script captures network packets and extracts metadata for analysis.
It focuses on identifying suspicious behavior, accessed domains, and
anomalous connections in your home network.

IMPORTANT: This tool captures METADATA only (not encrypted content).
It respects privacy and does not attempt to break encryption.

Author: Network Security Educational Project
License: MIT
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Scapy imports for packet capture and analysis
try:
    from scapy.all import (
        sniff, IP, TCP, UDP, DNS, DNSQR, ARP, Ether,
        conf, get_if_list, wrpcap, rdpcap
    )
    # Suppress Scapy verbose output
    conf.verb = 0
except ImportError:
    print("ERROR: Scapy not installed. Install with: pip install scapy")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MonitorConfig:
    """Configuration for the network monitor."""
    interface: str = ""  # Empty means auto-detect
    packet_count: int = 0  # 0 = infinite
    timeout: int = 300  # seconds, 0 = no timeout
    log_file: str = "network_traffic.log"
    pcap_file: str = "capture.pcap"
    dns_only: bool = False
    verbose: bool = True
    alert_threshold_bytes: int = 1000000  # 1MB threshold for alerts
    suspicious_ports: Set[int] = None
    
    def __post_init__(self):
        if self.suspicious_ports is None:
            # Common ports that may indicate suspicious activity
            self.suspicious_ports = {
                4444,  # Metasploit default
                5555,  # Android Debug Bridge
                6666,  # IRC (often used by malware)
                6667,  # IRC
                31337, # Back Orifice
                12345, # NetBus
                23,    # Telnet (insecure)
                3389,  # RDP (check for unauthorized access)
            }


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PacketMetadata:
    """Stores extracted metadata from a captured packet."""
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: str
    packet_size: int
    dns_query: Optional[str] = None
    flags: Optional[str] = None
    mac_src: Optional[str] = None
    mac_dst: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrafficSummary:
    """Aggregated traffic statistics."""
    total_packets: int = 0
    total_bytes: int = 0
    unique_ips: Set[str] = None
    dns_queries: List[str] = None
    connections: Dict[str, int] = None
    suspicious_events: List[dict] = None
    
    def __post_init__(self):
        if self.unique_ips is None:
            self.unique_ips = set()
        if self.dns_queries is None:
            self.dns_queries = []
        if self.connections is None:
            self.connections = defaultdict(int)
        if self.suspicious_events is None:
            self.suspicious_events = []


# =============================================================================
# NETWORK MONITOR CLASS
# =============================================================================

class NetworkMonitor:
    """
    Main network monitoring class.
    
    Captures packets, extracts metadata, and identifies suspicious activity.
    """
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.summary = TrafficSummary()
        self.ip_mac_map: Dict[str, str] = {}  # IP to MAC mapping
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the monitor."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Create logs directory
        log_dir = Path(self.config.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO if self.config.verbose else logging.WARNING,
            format=log_format,
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_available_interfaces(self) -> List[str]:
        """Get list of available network interfaces."""
        try:
            interfaces = get_if_list()
            self.logger.info(f"Available interfaces: {interfaces}")
            return interfaces
        except Exception as e:
            self.logger.error(f"Error getting interfaces: {e}")
            return []
    
    def extract_packet_metadata(self, packet) -> Optional[PacketMetadata]:
        """
        Extract metadata from a captured packet.
        
        This is the core function that analyzes each packet and extracts
        useful information without accessing encrypted content.
        """
        try:
            # Skip if packet doesn't have IP layer
            if not packet.haslayer(IP):
                return None
            
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            
            # Update IP tracking
            self.summary.unique_ips.add(src_ip)
            self.summary.unique_ips.add(dst_ip)
            
            # Track connection pairs
            conn_key = f"{src_ip}:{dst_ip}"
            self.summary.connections[conn_key] += 1
            
            # Extract port information
            src_port = None
            dst_port = None
            protocol = "IP"
            flags = None
            
            # Check for TCP
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                protocol = "TCP"
                flags = tcp_layer.flags
                
                # Check for suspicious ports
                if dst_port in self.config.suspicious_ports:
                    self.log_suspicious_activity(
                        f"Connection to suspicious port {dst_port}",
                        src_ip, dst_ip, dst_port
                    )
                
                # Check for high volume transfers
                if len(packet) > self.config.alert_threshold_bytes:
                    self.log_suspicious_activity(
                        f"Large packet detected ({len(packet)} bytes)",
                        src_ip, dst_ip, dst_port
                    )
            
            # Check for UDP
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                protocol = "UDP"
                
                # DNS over UDP (port 53)
                if dst_port == 53 or src_port == 53:
                    if packet.haslayer(DNS):
                        dns_query = self.extract_dns_query(packet)
                        if dns_query:
                            self.summary.dns_queries.append(dns_query)
                            self.logger.info(f"DNS Query: {dns_query}")
            
            # Get MAC addresses if available
            mac_src = None
            mac_dst = None
            if packet.haslayer(Ether):
                ether_layer = packet[Ether]
                mac_src = ether_layer.src
                mac_dst = ether_layer.dst
                
                # Update IP-MAC mapping
                if src_ip and mac_src:
                    self.ip_mac_map[src_ip] = mac_src
                if dst_ip and mac_dst:
                    self.ip_mac_map[dst_ip] = mac_dst
            
            # Update totals
            self.summary.total_packets += 1
            self.summary.total_bytes += len(packet)
            
            # Create metadata object
            metadata = PacketMetadata(
                timestamp=datetime.now().isoformat(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
                packet_size=len(packet),
                flags=str(flags) if flags else None,
                mac_src=mac_src,
                mac_dst=mac_dst
            )
            
            return metadata
            
        except Exception as e:
            self.logger.debug(f"Error extracting metadata: {e}")
            return None
    
    def extract_dns_query(self, packet) -> Optional[str]:
        """
        Extract DNS query from a packet.
        
        DNS queries are typically unencrypted and can reveal which
        domains devices are trying to access.
        """
        try:
            if packet.haslayer(DNSQR):
                dns_query = packet[DNSQR].qname.decode('utf-8', errors='ignore')
                return dns_query.rstrip('.')
        except Exception as e:
            self.logger.debug(f"Error extracting DNS: {e}")
        return None
    
    def log_suspicious_activity(self, description: str, src_ip: str, 
                                 dst_ip: str, port: Optional[int] = None):
        """Log suspicious activity for later analysis."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'SUSPICIOUS_ACTIVITY',
            'description': description,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'port': port
        }
        self.summary.suspicious_events.append(event)
        self.logger.warning(f"SUSPICIOUS: {description} | "
                           f"{src_ip} -> {dst_ip}:{port or 'N/A'}")
    
    def packet_callback(self, packet):
        """
        Callback function for each captured packet.
        
        This function is called by Scapy for every packet captured.
        """
        metadata = self.extract_packet_metadata(packet)
        
        if metadata and self.config.verbose:
            # Log packet summary
            self.logger.info(
                f"{metadata.protocol} | {metadata.src_ip}:{metadata.src_port or 'N/A'} -> "
                f"{metadata.dst_ip}:{metadata.dst_port or 'N/A'} | "
                f"{metadata.packet_size} bytes"
            )
    
    def start_capture(self):
        """
        Start packet capture.
        
        This is the main method that begins monitoring network traffic.
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting Network Monitor")
        self.logger.info("=" * 60)
        
        # Determine interface
        interface = self.config.interface
        if not interface:
            interfaces = self.get_available_interfaces()
            # Prefer eth0 or wlan0, otherwise use first non-lo interface
            for preferred in ['eth0', 'wlan0']:
                if preferred in interfaces:
                    interface = preferred
                    break
            if not interface:
                interface = interfaces[0] if interfaces else None
        
        if not interface:
            self.logger.error("No network interface found!")
            return
        
        self.logger.info(f"Using interface: {interface}")
        self.logger.info(f"Capture timeout: {self.config.timeout}s")
        self.logger.info(f"Packet count limit: {self.config.packet_count or 'unlimited'}")
        self.logger.info("=" * 60)
        
        try:
            # Start packet capture
            # BPF filter to reduce noise (optional optimization)
            bpf_filter = "ip" if self.config.dns_only else None
            
            sniff(
                iface=interface,
                prn=self.packet_callback,
                count=self.config.packet_count,
                timeout=self.config.timeout if self.config.timeout > 0 else None,
                store=False,  # Don't store packets in memory
                filter=bpf_filter
            )
            
        except PermissionError:
            self.logger.error(
                "Permission denied! Run with sudo or as root.\n"
                "In Docker, ensure you have --cap-add=NET_RAW --cap-add=NET_ADMIN"
            )
        except KeyboardInterrupt:
            self.logger.info("\nCapture interrupted by user")
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
        finally:
            self.save_results()
    
    def save_results(self):
        """Save capture results to files."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("SAVING RESULTS")
        self.logger.info("=" * 60)
        
        # Save summary as JSON
        summary_data = {
            'capture_end_time': datetime.now().isoformat(),
            'total_packets': self.summary.total_packets,
            'total_bytes': self.summary.total_bytes,
            'unique_ips': list(self.summary.unique_ips),
            'dns_queries': self.summary.dns_queries[:100],  # Limit to first 100
            'top_connections': sorted(
                self.summary.connections.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20],  # Top 20 connections
            'suspicious_events': self.summary.suspicious_events,
            'ip_mac_mapping': self.ip_mac_map
        }
        
        summary_file = Path(self.config.log_file).with_suffix('.json')
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        self.logger.info(f"Summary saved to: {summary_file}")
        
        # Print final statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print final capture statistics."""
        self.logger.info("\n--- CAPTURE STATISTICS ---")
        self.logger.info(f"Total Packets: {self.summary.total_packets}")
        self.logger.info(f"Total Bytes: {self.summary.total_bytes:,}")
        self.logger.info(f"Unique IPs: {len(self.summary.unique_ips)}")
        self.logger.info(f"DNS Queries Captured: {len(self.summary.dns_queries)}")
        self.logger.info(f"Suspicious Events: {len(self.summary.suspicious_events)}")
        
        if self.summary.suspicious_events:
            self.logger.info("\n--- SUSPICIOUS EVENTS ---")
            for event in self.summary.suspicious_events:
                self.logger.warning(
                    f"{event['timestamp']} - {event['description']}"
                )
        
        if self.summary.dns_queries:
            self.logger.info("\n--- TOP DNS QUERIES ---")
            # Count DNS query frequency
            dns_counts = defaultdict(int)
            for query in self.summary.dns_queries:
                dns_counts[query] += 1
            
            for domain, count in sorted(dns_counts.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True)[:10]:
                self.logger.info(f"  {count}x - {domain}")


# =============================================================================
# ARP SCANNER - Network Device Discovery
# =============================================================================

class ARPScanner:
    """
    ARP Scanner for discovering devices on the local network.
    
    This helps identify all devices connected to your network,
    which is crucial when suspecting unauthorized access.
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.devices: List[dict] = []
        
    def scan_network(self, target_ip: str = None) -> List[dict]:
        """
        Scan the local network for devices using ARP.
        
        Args:
            target_ip: Specific IP or range (e.g., "192.168.1.0/24")
                      If None, scans the local subnet
        """
        from scapy.all import ARP, Ether, srp
        
        if not target_ip:
            # Auto-detect local network
            target_ip = self._get_local_subnet()
            if not target_ip:
                print("Could not auto-detect local subnet. Please specify target_ip")
                return []
        
        print(f"Scanning network: {target_ip}")
        print("This may take 30-60 seconds...\n")
        
        try:
            # Create ARP request
            arp_request = ARP(pdst=target_ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast/arp_request
            
            # Send and receive responses
            answered, unanswered = srp(packet, timeout=3, verbose=0)
            
            # Process responses
            for sent, received in answered:
                device = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'vendor': self._identify_vendor(received.hwsrc)
                }
                self.devices.append(device)
                print(f"Found: {device['ip']} - {device['mac']} - {device['vendor']}")
            
            print(f"\nTotal devices found: {len(self.devices)}")
            return self.devices
            
        except Exception as e:
            print(f"Scan error: {e}")
            return []
    
    def _get_local_subnet(self) -> Optional[str]:
        """Auto-detect local subnet from default gateway."""
        import socket
        import struct
        
        try:
            # Get default gateway IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Derive /24 subnet
            parts = local_ip.split('.')
            subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            
            print(f"Detected local IP: {local_ip}")
            print(f"Scanning subnet: {subnet}")
            
            return subnet
            
        except Exception as e:
            print(f"Error detecting subnet: {e}")
            return None
    
    def _identify_vendor(self, mac: str) -> str:
        """Identify vendor from MAC address OUI."""
        # Common vendor OUIs (first 3 octets)
        vendors = {
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '52:54:00': 'QEMU',
            '00:1C:42': 'Parallels',
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Intel',
            '00:1A:2B': 'Apple',
            '3C:5A:B4': 'Google',
            'F0:B4:79': 'Amazon',
        }
        
        oui = mac[:8].upper()
        return vendors.get(oui, 'Unknown')
    
    def export_devices(self, filename: str = "network_devices.json"):
        """Export discovered devices to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                'scan_time': datetime.now().isoformat(),
                'devices': self.devices
            }, f, indent=2)
        print(f"Device list saved to: {filename}")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main entry point for the network monitor."""
    parser = argparse.ArgumentParser(
        description='Network Monitor - Educational Packet Capture Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic monitoring (300 seconds)
  python network_monitor.py
  
  # Monitor specific interface
  python network_monitor.py -i eth0
  
  # DNS-only monitoring
  python network_monitor.py --dns-only
  
  # Scan network for devices
  python network_monitor.py --scan
  
  # Custom timeout and log file
  python network_monitor.py -t 600 -l my_capture.log
        """
    )
    
    parser.add_argument('-i', '--interface', type=str, default='',
                       help='Network interface to monitor')
    parser.add_argument('-t', '--timeout', type=int, default=300,
                       help='Capture timeout in seconds (0 = unlimited)')
    parser.add_argument('-c', '--count', type=int, default=0,
                       help='Number of packets to capture (0 = unlimited)')
    parser.add_argument('-l', '--log-file', type=str, default='network_traffic.log',
                       help='Log file path')
    parser.add_argument('--pcap', type=str, default='capture.pcap',
                       help='PCAP file for saving raw packets')
    parser.add_argument('--dns-only', action='store_true',
                       help='Only capture DNS traffic')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--scan', action='store_true',
                       help='Run ARP scan instead of packet capture')
    parser.add_argument('--target', type=str,
                       help='Target IP/range for ARP scan')
    
    args = parser.parse_args()
    
    # Print banner
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           NETWORK MONITOR - EDUCATIONAL TOOL             ║
    ║                                                          ║
    ║  For defensive monitoring of YOUR OWN network only      ║
    ║  Respects privacy - captures metadata only              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    if args.scan:
        # Run ARP scanner
        print("=== ARP Network Scanner ===\n")
        scanner = ARPScanner(interface=args.interface)
        scanner.scan_network(args.target)
        scanner.export_devices()
    else:
        # Run packet capture
        config = MonitorConfig(
            interface=args.interface,
            timeout=args.timeout,
            packet_count=args.count,
            log_file=args.log_file,
            pcap_file=args.pcap,
            dns_only=args.dns_only,
            verbose=not args.quiet
        )
        
        monitor = NetworkMonitor(config)
        
        # Show available interfaces if none specified
        if not args.interface:
            interfaces = monitor.get_available_interfaces()
            print(f"\nAvailable interfaces: {interfaces}\n")
        
        monitor.start_capture()
    
    print("\nDone! Check the log files for detailed analysis.")


if __name__ == '__main__':
    main()
