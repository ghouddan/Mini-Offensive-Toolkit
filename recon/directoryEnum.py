import requests
import concurrent.futures
import pyfiglet
import sys 
from datetime import datetime
import itertools




def pars_word_list(file_path):
    parsed_word_list=[]
    with open(file_path, 'r') as file:
        for line in file:
            parsed_word_list.append(line.strip())
    return parsed_word_list

def send_request(url,directory,extention=""):
    if extention:
        directory = f"{directory}.{extention}"

    full_url = f"{url}/{directory}"
    try:
        response = requests.get(full_url, timeout=5)
        if response.status_code == 200:
            return full_url, response.status_code, "Found"
        elif response.status_code in [301, 302, 307, 308]:  # Redirects
            return full_url, response.status_code, f"Redirect to {response.headers.get('Location', 'Unknown')}"
        elif response.status_code == 403:
            return full_url, response.status_code, "Forbidden (exists but access denied)"
        else:
            return full_url, response.status_code, f"Status: {response.status_code}" 
    except requests.exceptions.Timeout:
        return full_url, "TIMEOUT", "Request timed out"
    except requests.exceptions.RequestException as e:
        return full_url, "ERROR", f"Request error: {str(e)}"
    except Exception as e:
        return full_url, "ERROR", f"Unexpected error: {str(e)}"

def directory_enum(target_url, word_list_path,extention=None):
    directory_list = pars_word_list(word_list_path)
    if extention is None:
        extention = [""]

    print("=" * 60)
    asscii_banner = pyfiglet.figlet_format("DirEnum")
    print(asscii_banner)
    print("=" * 60)
    print(f"Target Domain: {target_url}")
    print(f"Wordlist: {word_list_path}")
    #print(f"Max Workers: {max_workers}")
    print(f"Started at: {datetime.now()}")
    print("=" * 60)
    
    directories = len(directory_list)
    print(f"Loaded {directories} subdomains from wordlist")
    print("Starting enumeration...")
    print("-" * 60)
    found_directory =[]
    completed = 0

    try :
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_direcotory = {
                    executor.submit(send_request, target_url, directory, extention): (directory, extention)
                    for directory, extention in itertools.product(directory_list, extention)            
                }
            for Future in concurrent.futures.as_completed(future_to_direcotory):
                directory = future_to_direcotory[Future]
                completed += 1
                try:
                    url , status_code, message = Future.result()
                    if status_code == 200 or status_code== 403 or 'Redirect' in message:
                        found_directory.append((url, status_code, message))
                        print(f"[{completed}/{len(directory_list)}] {url} - {status_code} - {message}")

                except Exception as e :
                    print(f"Error occurred for directory {directory}: {str(e)}")
    except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user. Exiting...")
            sys.exit(0)

    print("\n" + "=" * 60)
    print("ENUMERATION COMPLETE")
    print("=" * 60)
    print(f"Total directories tested: {directories}")
    print(f"Found directories: {len(found_directory)}")
    print(f"Completed at: {datetime.now()}")
    

    if found_directory:
        print("\nDISCOVERED DIRECTORIES:")
        print("-" * 60)

        for url, status_code, message in found_directory:
            print(f"{url} - {status_code} - {message}")
    else:
        print("\n[!] No directory found. Try a different wordlist or check the target domain.")




if __name__ == "__main__":
    path="/home/mo/Desktop/Offensive-ToolKit/recon/wordlist.txt"
    url="https://google.com"
    extention=["php","html"]
    directory_enum(url,path,extention)