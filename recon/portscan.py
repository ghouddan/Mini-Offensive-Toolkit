import socket
import sys
import ipaddress

def pars_port_range(range_str):
    if '-' in range_str:
        start, end = map(int, range_str.split('-'))
        return start, end
    elif ',' in range_str:
        ports = list(map(int, range_str.split(',')))
        return ports
    
def parss_ip_address(ip_str):
    try:
        network = ipaddress.ip_network(ip_str, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Invalid CIDR: {e}")
        return []
        

def port_scanner(target,rang):
    try:
        if '-' in rang or '/' in target:
            start, end = pars_port_range(rang)
            ips= parss_ip_address(target)
            for ip in ips:
                print(f"Scanning IP: {ip}")
                for port in range(start,end+1):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    result = s.connect_ex((ip,port))
                    if result == 0:
                        print("Port {} is open".format(port))
                    else:
                        pass
                    s.close()

        elif ',' in rang or '/' in target:
            ips= parss_ip_address(target)
            ports = pars_port_range(rang)
            for ip in ips:
                for port in ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    result = s.connect_ex((ip,port))
                    if result == 0:
                        print("Port {} is open".format(port))
                    else:
                        print("Port {} is closed".format(port))
                    s.close()
            
    except KeyboardInterrupt:
        print("\n Exiting Program !!!!")
        sys.exit()
    except s.gaierror:
        print("\n Hostname Could Not Be Resolved !!!!")
        sys.exit()
    except s.error:
        print("\ Server not responding !!!!")
        sys.exit()

if __name__ =="__main__":
    target = input("Enter Target IP Address : ")
    rang = str(input("Enter range of port to scan : "))
    port_scanner(target,rang)




"""socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.settimeout(1)
result = socket.connect_ex(("127.0.0.1",444))
if result == 0:
    print("Port is open")
else:
    print("Port is closed")"""