import os
import platform
import sys

BLOCKED_SITES = [
    "youtube.com",
    "www.youtube.com"
]

REDIRECT_IP = "127.0.0.1"

def get_hosts_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif system in ["Linux", "Darwin"]:  
        return "/etc/hosts"
    else:
        raise Exception("Unsupported OS")

def modify_hosts(block=True):
    hosts_path = get_hosts_path()
    try:
        with open(hosts_path, "r+", encoding="utf-8") as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()

            already_blocked = set()
            for line in lines:
                if any(site in line for site in BLOCKED_SITES):
                    if not block:
                        continue  # remove line
                    already_blocked.add(line.strip())
                file.write(line)

            if block:
                for site in BLOCKED_SITES:
                    entry = f"{REDIRECT_IP} {site}\n"
                    if entry.strip() not in already_blocked:
                        file.write(entry)
                        print(f"[+] Blocked {site}")
            else:
                print("[✓] Unblocked selected sites.")
    except PermissionError:
        print("[!] Run this script as administrator/root.")
        sys.exit(1)

def flush_dns_cache():
    system = platform.system()
    try:
        if system == "Windows":
            os.system("ipconfig /flushdns")
        elif system == "Linux":
            os.system("sudo systemd-resolve --flush-caches")
        elif system == "Darwin":  # macOS
            os.system("sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")
        print("[✓] DNS cache flushed.")
    except Exception as e:
        print(f"[!] Error flushing DNS cache: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n  python site_blocker.py block\n  python site_blocker.py unblock")
        sys.exit(0)

    action = sys.argv[1].lower()

    if action == "block":
        modify_hosts(block=True)
        flush_dns_cache()
    elif action == "unblock":
        modify_hosts(block=False)
        flush_dns_cache()
    else:
        print("Invalid command. Use 'block' or 'unblock'.")
