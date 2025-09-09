import socket
import sys
import ipaddress
import pyfiglet
from datetime import datetime
import concurrent.futures


# Common port-to-service mapping
SERVICE_MAP = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL",
    3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 9200: "Elasticsearch"
}


def parse_port_range(range_str):
    if '-' in range_str:
        start, end = map(int, range_str.split('-'))
        return list(range(start, end + 1))
    elif ',' in range_str:
        return list(map(int, range_str.split(',')))
    else:
        return [int(range_str)]


def parse_ip_address(ip_str):
    try:
        network = ipaddress.ip_network(ip_str, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Invalid CIDR: {e}")
        return []


def get_service_name(port):
    """Get service name for a port"""
    return SERVICE_MAP.get(port, "Unknown")


def grab_banner(sock, port):
    """Grab banner from an open socket"""
    try:
        # Set a shorter timeout for banner grabbing
        sock.settimeout(2)
        
        # Send appropriate probe based on port
        if port in [80, 8080, 8000]:
            # HTTP probe
            sock.send(b"GET / HTTP/1.1\r\nHost: target\r\n\r\n")
        elif port == 21:
            # FTP - just wait for welcome message
            pass
        elif port == 25:
            # SMTP probe
            sock.send(b"HELO test\r\n")
        elif port == 22:
            # SSH - just wait for banner
            pass
        else:
            # Generic probe for other services
            sock.send(b"\r\n")
        
        # Try to receive banner
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        
        # Clean up banner (first line only, max 100 chars)
        if banner:
            banner = banner.split('\n')[0].split('\r')[0][:100]
            return banner if banner else "No banner"
        else:
            return "No banner"
            
    except socket.timeout:
        return "Timeout"
    except Exception:
        return "Error"


def scan_port_and_get_banner(target, port):
    """Scan a port and get banner if open"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        
        # Check if port is open
        result = s.connect_ex((target, port))
        
        if result == 0:  # Port is open
            service = get_service_name(port)
            banner = grab_banner(s, port)
            s.close()
            return port, True, service, banner
        else:
            s.close()
            return port, False, "", ""
            
    except Exception:
        return port, False, "", ""


def display_banner(target, port_count):
    """Display banner and scan info"""
    ascii_banner = pyfiglet.figlet_format("Port Scanner")
    print(ascii_banner)
    print('-' * 60)
    print(f"Target: {target}")
    print(f"Scanning {port_count} ports")
    print(f"Starting scan at: {datetime.now()}")
    print('-' * 60)


def port_scanner(target, range_str):
    try:
        # Parse targets and ports
        if '/' in target:
            ips = parse_ip_address(target)
        else:  
            ips = [target]
        
        ports = parse_port_range(range_str)
        
        # Scan each IP
        for ip in ips:
            if len(ips) > 1:
                print(f"\nScanning IP: {ip}")
            
            # Display banner
            display_banner(ip, len(ports))
            
            open_ports_info = []
            
            # Use ThreadPoolExecutor for concurrent scanning
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                # Submit all scanning tasks (now includes banner grabbing)
                future_to_port = {
                    executor.submit(scan_port_and_get_banner, ip, port): port 
                    for port in ports
                }
                
                # Collect results as they complete
                completed = 0
                for future in concurrent.futures.as_completed(future_to_port):
                    port, is_open, service, banner = future.result()
                    if is_open:
                        open_ports_info.append((port, service, banner))
                    
                    # Simple progress indicator
                    completed += 1
                    if completed % 100 == 0 or completed == len(ports):
                        print(f"Progress: {completed}/{len(ports)} ports scanned")
            
            # Display results after all threads finish
            print('\n' + '=' * 60)
            print(f"SCAN RESULTS FOR {ip}")
            print('=' * 60)
            
            if open_ports_info:
                # Sort by port number
                open_ports_info.sort(key=lambda x: x[0])
                print(f"Open ports ({len(open_ports_info)}):")
                print()
                
                # Display with formatting
                for port, service, banner in open_ports_info:
                    service_info = f"[{service}]" if service != "Unknown" else ""
                    banner_info = f" - {banner}" if banner and banner not in ["No banner", "Timeout", "Error"] else ""
                    
                    print(f"  Port {port:<5} {service_info:<15} OPEN{banner_info}")
            else:
                print("No open ports found")
            
            print(f"\nScan completed at: {datetime.now()}")
            print('=' * 60)
            
    except KeyboardInterrupt:
        print("\nExiting Program!")
        sys.exit()


if __name__ == "__main__":
    target = input("Enter Target IP Address: ")
    range_input = input("Enter range or port to scan: ")
    port_scanner(target, range_input)