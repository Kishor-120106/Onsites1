import os
import time
import psutil
import shutil
import sqlite3
from datetime import datetime, timedelta


CHECK_INTERVAL = 30  
MAX_ENTRIES = 50     
CHROME_PROCESS = "chrome.exe"
LOG_FILE = "visited_sites_log.txt"


def get_chrome_history_path():
    return os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\History')


def chrome_time_to_datetime(chrome_time):
    """Convert Chrome timestamp to readable datetime."""
    epoch_start = datetime(1601, 1, 1)
    return epoch_start + timedelta(microseconds=chrome_time)


def log_entries_to_file(entries):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for url, title, visit_time in entries:
            f.write(f"[{visit_time}] {title} - {url}\n")


def extract_chrome_history():
    try:
        src_path = get_chrome_history_path()
        temp_path = "History_temp"
        shutil.copy2(src_path, temp_path)

        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT url, title, last_visit_time 
            FROM urls 
            ORDER BY last_visit_time DESC 
            LIMIT {MAX_ENTRIES}
        """)
        entries = []
        for url, title, visit_time in cursor.fetchall():
            dt = chrome_time_to_datetime(visit_time)
            entries.append((url, title, dt.strftime('%Y-%m-%d %H:%M:%S')))
        conn.close()
        os.remove(temp_path)
        return entries
    except Exception as e:
        print("Error reading Chrome history:", e)
        return []


def is_chrome_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == CHROME_PROCESS.lower():
            return True
    return False


def track_websites():
    print("[*] Website tracking started...")
    seen_urls = set()

    while True:
        if is_chrome_running():
            entries = extract_chrome_history()
            new_entries = []

            for url, title, visit_time in entries:
                if url not in seen_urls:
                    new_entries.append((url, title, visit_time))
                    seen_urls.add(url)

            if new_entries:
                log_entries_to_file(new_entries)
                print(f"[+] Logged {len(new_entries)} new websites.")
        else:
            print("[!] Chrome not running...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    track_websites()
