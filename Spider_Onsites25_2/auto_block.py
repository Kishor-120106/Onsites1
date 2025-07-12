import os
import sys
import time
import platform
from datetime import datetime, timedelta
from collections import defaultdict


LOG_FILE = "visited_sites_log.txt"
BLOCK_THRESHOLD = 2
TIME_WINDOW = timedelta(hours=1)
REDIRECT_IP = "127.0.0.1"
CHECK_INTERVAL = 60  


def get_hosts_path():
    if platform.system() == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif platform.system() in ["Linux", "Darwin"]:  
        return "/etc/hosts"
    else:
        raise Exception("Unsupported OS")


def flush_dns_cache():
    system = platform.system()
    if system == "Windows":
        os.system("ipconfig /flushdns")
    elif system == "Linux":
        os.system("sudo systemd-resolve --flush-caches")
    elif system == "Darwin":
        os.system("sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")
    print(" DNS cache flushed")


def block_site(domain):
    hosts_path = get_hosts_path()
    try:
        with open(hosts_path, "r+", encoding="utf-8") as file:
            lines = file.readlines()
            already_blocked = any(domain in line for line in lines)

            if not already_blocked:
                file.write(f"{REDIRECT_IP} {domain}\n")
                print(f" Blocked {domain}")
    except PermissionError:
        print("[!] Permission denied: Run this script as administrator/root")
        sys.exit(1)


def parse_log_file():
    site_visits = defaultdict(list)
    now = datetime.now()

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    timestamp_str, rest = line.strip().split("] ", 1)
                    timestamp_str = timestamp_str.strip("[")
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    title, url = rest.rsplit(" - ", 1)
                    domain = url.split("//")[-1].split("/")[0]
                    if now - timestamp <= TIME_WINDOW:
                        site_visits[domain].append(timestamp)
                except Exception as e:
                    continue  
    except FileNotFoundError:
        print("[!] Log file not found.")
    return site_visits


def auto_block_monitor():
    print("[*] Auto-block monitor started...")

    already_blocked = set()

    while True:
        visits = parse_log_file()

        for domain, timestamps in visits.items():
            if len(timestamps) > BLOCK_THRESHOLD and domain not in already_blocked:
                block_site(domain)
                flush_dns_cache()
                already_blocked.add(domain)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    auto_block_monitor()
