import requests
import sys
import concurrent.futures 
from datetime import datetime
import pyfiglet


def pars_word_list(file):
    words = []
    with open(file,'r') as f:
        for line in f:
            words.append(line.strip())
    return words


def send_request(sub_domain, domain_name):
    url= f"https://{sub_domain}.{domain_name}"

    try:
        r = requests.get(url, timeout=3,allow_redirects=True)
        if r.status_code == 200:
            return url, r.status_code, "Found"
        elif r.status_code in [301, 302, 307, 308]:  # Redirects
            return url, r.status_code, f"Redirect to {r.headers.get('Location', 'Unknown')}"
        elif r.status_code == 403:
            return url, r.status_code, "Forbidden (exists but access denied)"
        else:
            return url, r.status_code, f"Status: {r.status_code}" 
        
    except requests.exceptions.SSLError:
        try:
            http_url = f"http://{sub_domain}.{domain_name}"
            r = requests.get(http_url, timeout=3, allow_redirects=True)
            if r.status_code == 200:
                return http_url, r.status_code, "Found (HTTP)"
        except :
            pass
        return None , None, None 
    except requests.exceptions.ConnectionError:
        return None , None, None
    
    except requests.exceptions.Timeout:
        return url, "TIMEOUT", "Request timed out"
    
    except requests.exceptions.RequestException as e:
        return url, "ERROR", f"Request error: {str(e)}"
        
    except Exception as e:
        return url, "ERROR", f"Unexpected error: {str(e)}"



def subenum(domain_name,word_list_path):

    print("=" * 60)
    asscii_banner = pyfiglet.figlet_format("SubEnum")
    print(asscii_banner)
    print("=" * 60)
    print(f"Target Domain: {domain_name}")
    print(f"Wordlist: {word_list_path}")
    #print(f"Max Workers: {max_workers}")
    print(f"Started at: {datetime.now()}")
    print("=" * 60)
    
    # Parse wordlist
    sublist = pars_word_list(word_list_path)

    total_subdomains = len(sublist)
    print(f"Loaded {total_subdomains} subdomains from wordlist")
    print("Starting enumeration...")
    print("-" * 60)
    found_subdomains = []
    completed = 0
    try :
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_subdomain = {
                    executor.submit(send_request, sub_domain, domain_name): sub_domain
                    for sub_domain in sublist
                }
                for future in concurrent.futures.as_completed(future_to_subdomain):
                    sub_domain = future_to_subdomain[future]
                    complete = +1

                    try:
                        url,status_code,message = future.result()

                        if url and status_code:
                            found_subdomains.append((url,status_code,message))
                            print(f"[+][{status_code}] {url} - {message}")   
                    except Exception as e:
                        print(f"[!] Error checking {sub_domain}: {str(e)}")    

    except KeyboardInterrupt:
                    print("\n[!] Scan interrupted by user. Exiting...")
                    sys.exit(0)
# Display final results
    print("\n" + "=" * 60)
    print("ENUMERATION COMPLETE")
    print("=" * 60)
    print(f"Total subdomains tested: {total_subdomains}")
    print(f"Found subdomains: {len(found_subdomains)}")
    print(f"Completed at: {datetime.now()}")
    
    if found_subdomains:
        print("\nDISCOVERED SUBDOMAINS:")
        print("-" * 60)
        
        # Sort results by status code
        found_subdomains.sort(key=lambda x: x[1])
        
        for url, status_code, description in found_subdomains:
            print(f" [+] {url:<40} [{status_code}] {description}")
    else:
        print("\n[!] No subdomains found. Try a different wordlist or check the target domain.")
    
    print("=" * 60)


if __name__ == "__main__":
    path = "/home/mo/Desktop/Offensive-ToolKit/recon/wordlist.txt"
    domain_name = "google.com"
    subenum(domain_name, path)
