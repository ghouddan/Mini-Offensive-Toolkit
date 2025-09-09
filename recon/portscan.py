import socket
import sys
import ipaddress
import pyfiglet
from datetime import datetime


def pars_port_range(range_str):
    if '-' in range_str:
        start, end = map(int, range_str.split('-'))
        return list(rang((start, end + 1)))
    elif ',' in range_str:
        return  list(map(int, range_str.split(',')))
    else:
        return [int(range_str)]


def parss_ip_address(ip_str):
    try:
        network = ipaddress.ip_network(ip_str, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Invalid CIDR: {e}")
        return []
        
def scan_single_port(target, port):
    assci_banner = pyfiglet.figlet_format("Port Scanner")
    print(assci_banner)
    print('-'*60)
    print("staring scan at:" + str(datetime.now()))
    print('-'*60)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((target, port))
        s.close()  # Always close after each attempt
        return result == 0
    except Exception:
        return False

def port_scanner(target,rang):
    try:
        if '/' in target:
            ips = parss_ip_address(target)
        else:  
            ips = [target]
        
        ports = pars_port_range(rang)
        for  ip in ips:
            if len(ips)>1:
                print(f"Scanning IP: {ip}")
            for port in ports:
                if scan_single_port(ip,port):
                    print(f"Port {port} is open on {ip}")
                else:
                    print(f"Port {port} is closed on {ip}")
    except KeyboardInterrupt:
        print("\nExiting Program!")
        sys.exit()


if __name__ =="__main__":
    target = input("Enter Target IP Address : ")
    rang = str(input("Enter range or port to scan : "))
    port_scanner(target,rang)




"""socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.settimeout(1)
result = socket.connect_ex(("127.0.0.1",444))
if result == 0:
    print("Port is open")
else:
    print("Port is closed")"""