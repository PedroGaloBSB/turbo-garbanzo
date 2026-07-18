#!/bin/bash
# =============================================================================
# Quick Start Script - Network Monitor
# =============================================================================
# This script automates the initial setup and execution of the network monitor.
# It checks dependencies, creates necessary directories, and offers menu options.
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         NETWORK MONITOR - QUICK START SCRIPT             ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Dependency Checks
# =============================================================================

check_dependencies() {
    echo "Checking dependencies..."
    echo ""
    
    local missing_deps=()
    
    # Check Python
    if check_command python3; then
        print_success "Python 3: $(python3 --version)"
    else
        missing_deps+=("python3")
        print_error "Python 3 not found"
    fi
    
    # Check pip
    if check_command pip3; then
        print_success "pip3: $(pip3 --version | head -1)"
    else
        missing_deps+=("python3-pip")
        print_error "pip3 not found"
    fi
    
    # Check Docker (optional)
    if check_command docker; then
        print_success "Docker: $(docker --version)"
    else
        print_warning "Docker not found (optional for Option B)"
    fi
    
    # Check Docker Compose (optional)
    if check_command docker-compose || check_command "docker compose"; then
        print_success "Docker Compose available"
    else
        print_warning "Docker Compose not found (optional for Option B)"
    fi
    
    # Check tcpdump (optional but useful)
    if check_command tcpdump; then
        print_success "tcpdump available"
    else
        print_warning "tcpdump not found (useful for PCAP analysis)"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo ""
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Install with:"
        echo "  Debian/Ubuntu: sudo apt-get install -y ${missing_deps[*]}"
        echo "  Fedora/RHEL:   sudo dnf install -y ${missing_deps[*]}"
        echo "  Arch:          sudo pacman -S ${missing_deps[*]}"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo ""
}

install_python_deps() {
    echo "Installing Python dependencies..."
    cd "$PROJECT_ROOT/python-scapy"
    
    if pip3 install -r requirements.txt; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        echo "Try running with sudo: sudo pip3 install -r requirements.txt"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
}

create_directories() {
    echo "Creating directory structure..."
    
    mkdir -p "$PROJECT_ROOT/docker-compose/pihole/etc-pihole"
    mkdir -p "$PROJECT_ROOT/docker-compose/pihole/etc-dnsmasq.d"
    mkdir -p "$PROJECT_ROOT/docker-compose/logs/pihole"
    mkdir -p "$PROJECT_ROOT/docker-compose/logs/monitor"
    mkdir -p "$PROJECT_ROOT/docker-compose/captures"
    mkdir -p "$PROJECT_ROOT/docker-compose/grafana/data"
    
    print_success "Directories created"
}

# =============================================================================
# Menu Options
# =============================================================================

show_menu() {
    echo ""
    echo "Choose an option:"
    echo ""
    echo "  1) Run Python Network Monitor (Option A)"
    echo "  2) Run ARP Scanner"
    echo "  3) Start Docker Compose Stack (Option B)"
    echo "  4) View Pi-hole Logs"
    echo "  5) View Network Monitor Logs"
    echo "  6) Analyze Capture Results"
    echo "  7) Security Checklist"
    echo "  8) Exit"
    echo ""
}

run_python_monitor() {
    echo ""
    echo "Running Python Network Monitor..."
    echo ""
    echo "Options:"
    echo "  1) Quick scan (60 seconds)"
    echo "  2) Standard scan (5 minutes)"
    echo "  3) Extended scan (30 minutes)"
    echo "  4) DNS only mode"
    echo "  5) Custom configuration"
    echo ""
    read -p "Choose option (1-5): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" -t 60
            ;;
        2)
            sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" -t 300
            ;;
        3)
            sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" -t 1800
            ;;
        4)
            sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" --dns-only -t 300
            ;;
        5)
            echo "Enter custom timeout (seconds): "
            read timeout
            echo "Enter interface (leave empty for auto): "
            read interface
            
            cmd="sudo python3 $PROJECT_ROOT/python-scapy/network_monitor.py -t $timeout"
            [ -n "$interface" ] && cmd="$cmd -i $interface"
            $cmd
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

run_arp_scanner() {
    echo ""
    echo "Running ARP Network Scanner..."
    echo ""
    echo "Enter target network (e.g., 192.168.1.0/24) or press Enter for auto-detect:"
    read target
    
    if [ -n "$target" ]; then
        sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" --scan --target "$target"
    else
        sudo python3 "$PROJECT_ROOT/python-scapy/network_monitor.py" --scan
    fi
    
    echo ""
    echo "Results saved to: network_devices.json"
}

start_docker_compose() {
    echo ""
    echo "Starting Docker Compose stack..."
    echo ""
    
    cd "$PROJECT_ROOT/docker-compose"
    
    # Create directories if not exist
    create_directories
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        return 1
    fi
    
    # Warn about password
    echo -e "${YELLOW}IMPORTANT: Edit docker-compose.yml to change WEBPASSWORD before starting!${NC}"
    echo ""
    read -p "Have you changed the default password? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Please edit docker-compose.yml and change WEBPASSWORD"
        echo "Press any key to continue anyway..."
        read -n 1
    fi
    
    # Start services
    docker-compose up -d
    
    echo ""
    print_success "Services started!"
    echo ""
    echo "Access points:"
    echo "  - Pi-hole Admin: http://localhost/admin (password: ChangeMe123!)"
    echo "  - Grafana:       http://localhost:3000 (if using monitoring profile)"
    echo ""
    echo "Commands:"
    echo "  docker-compose ps          # Check status"
    echo "  docker-compose logs -f     # View logs"
    echo "  docker-compose down        # Stop services"
    echo ""
    
    cd "$SCRIPT_DIR"
}

view_logs() {
    echo ""
    echo "Select log source:"
    echo "  1) Pi-hole logs"
    echo "  2) Network Monitor logs"
    echo "  3) Live tail (continuous)"
    echo ""
    read -p "Choose option (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            cd "$PROJECT_ROOT/docker-compose"
            docker-compose logs pihole | less
            ;;
        2)
            cd "$PROJECT_ROOT/docker-compose"
            docker-compose logs network-monitor | less
            ;;
        3)
            cd "$PROJECT_ROOT/docker-compose"
            docker-compose logs -f
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
}

analyze_results() {
    echo ""
    echo "Analyzing capture results..."
    echo ""
    
    if [ ! -f "$PROJECT_ROOT/docker-compose/logs/monitor/network_traffic.json" ]; then
        print_error "No capture results found. Run the monitor first."
        return 1
    fi
    
    echo "=== TOP DNS QUERIES ==="
    cat "$PROJECT_ROOT/docker-compose/logs/monitor/network_traffic.json" | \
        python3 -c "import sys,json; data=json.load(sys.stdin); 
queries=data.get('dns_queries',[]); 
from collections import Counter; 
counts=Counter(queries); 
for domain,count in counts.most_common(10): 
    print(f'{count:5d}x - {domain}')"
    
    echo ""
    echo "=== SUSPICIOUS EVENTS ==="
    cat "$PROJECT_ROOT/docker-compose/logs/monitor/network_traffic.json" | \
        python3 -c "import sys,json; data=json.load(sys.stdin); 
events=data.get('suspicious_events',[]); 
if events:
    for e in events: 
        print(f\"{e['timestamp']} - {e['description']}\");
else:
    print('No suspicious events detected')"
    
    echo ""
    echo "=== CONNECTION STATISTICS ==="
    cat "$PROJECT_ROOT/docker-compose/logs/monitor/network_traffic.json" | \
        python3 -c "import sys,json; data=json.load(sys.stdin); 
print(f'Total Packets: {data.get(\"total_packets\",0)}'); 
print(f'Total Bytes: {data.get(\"total_bytes\",0):,}'); 
print(f'Unique IPs: {len(data.get(\"unique_ips\",[]))}')"
}

security_checklist() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              SECURITY CHECKLIST                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    checklist=(
        "Change Wi-Fi password to strong passphrase (20+ chars)"
        "Change router admin password"
        "Disable WPS on router"
        "Update router firmware"
        "Disable remote administration on router"
        "Enable WPA2/WPA3 encryption"
        "Create separate guest network for visitors"
        "Isolate IoT devices on separate VLAN/network"
        "Review port forwarding rules on router"
        "Check for unknown devices on network"
        "Enable 2FA on all important accounts"
        "Review browser extensions"
        "Check startup programs and scheduled tasks"
        "Verify SSH authorized_keys"
        "Run network monitor to detect anomalies"
    )
    
    for i in "${!checklist[@]}"; do
        echo "[ ] ${checklist[$i]}"
    done
    
    echo ""
    echo "Copy this checklist and mark items as you complete them."
    echo "Save to security_checklist.txt for tracking."
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    print_header
    
    # Pre-flight checks
    check_dependencies
    install_python_deps
    create_directories
    
    # Main menu loop
    while true; do
        show_menu
        read -p "Enter choice (1-8): " -n 1 -r
        echo
        
        case $REPLY in
            1) run_python_monitor ;;
            2) run_arp_scanner ;;
            3) start_docker_compose ;;
            4|5) view_logs ;;
            6) analyze_results ;;
            7) security_checklist ;;
            8) 
                echo "Goodbye!"
                exit 0
                ;;
            *) print_error "Invalid option" ;;
        esac
        
        echo ""
        echo "Press any key to continue..."
        read -n 1
    done
}

# Run main function
main "$@"
