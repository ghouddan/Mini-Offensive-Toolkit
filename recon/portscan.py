import socket
import sys
import ipaddress
import pyfiglet
from datetime import datetime
import concurrent.futures


def parse_port_range(range_str):
    if '-' in range_str:
        start, end = map(int, range_str.split('-'))
        return list(range(start, end + 1))  # Fixed: was 'rang'
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
        

def scan_single_port(target, port):
    """Scan a single port and return the result"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((target, port))
        s.close()
        return result == 0
    except Exception:
        return False


def display_banner(target, port_count):
    """Display banner and scan info"""
    ascii_banner = pyfiglet.figlet_format("Port Scanner")
    print(ascii_banner)
    print('-' * 60)
    print(f"Target: {target}")
    print(f"Scanning {port_count} ports")
    print(f"Starting scan at: {datetime.now()}")
    print('-' * 60)


def scan_port_with_result(target, port):
    """Wrapper function that returns port and result"""
    result = scan_single_port(target, port)
    return port, result


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
            
            open_ports = []
            
            # Use ThreadPoolExecutor for concurrent scanning
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                # Submit all scanning tasks
                future_to_port = {
                    executor.submit(scan_port_with_result, ip, port): port 
                    for port in ports
                }
                
                # Collect results as they complete
                completed = 0
                for future in concurrent.futures.as_completed(future_to_port):
                    port, is_open = future.result()
                    if is_open:
                        open_ports.append(port)
                    
                    # Simple progress indicator
                    completed += 1
                    if completed % 100 == 0 or completed == len(ports):
                        print(f"Progress: {completed}/{len(ports)} ports scanned")
            
            # Display results after all threads finish
            print('\n' + '=' * 60)
            print(f"SCAN RESULTS FOR {ip}")
            print('=' * 60)
            
            if open_ports:
                open_ports.sort()  # Sort ports for better readability
                print(f"Open ports ({len(open_ports)}):")
                for port in open_ports:
                    print(f"  Port {port} is OPEN")
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