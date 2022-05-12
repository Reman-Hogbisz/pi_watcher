import requests
import feedparser
import os
from datetime import datetime, timedelta
from time import sleep, mktime


RSS_URL = None
WEBHOOK_URL = None

LAST_CHECKED = datetime.now() - timedelta(hours=1)


def filter_entry(entry):
    time = datetime.fromtimestamp(mktime(entry['published_parsed']))
    return time > LAST_CHECKED


def check_url():
    feed_response = feedparser.parse(RSS_URL)
    last_built = datetime.fromtimestamp(
        mktime(feed_response['feed']['updated_parsed']))
    if last_built < LAST_CHECKED:
        print("[-] No new posts")
        return

    entries = list(filter(filter_entry, feed_response['entries']))
    length_of_entries = len(entries)

    if length_of_entries > 0:
        print(f"[+] New posts found (found {length_of_entries})")

    for entry in entries:
        title = entry['title']
        link = entry['link']
        print(f"\t[+] Got new entry: {title}\n\t\t{link}")
        requests.post(WEBHOOK_URL, json={
            "content": f"{title}\n{link}"})


if __name__ == "__main__":
    print("[+] Started watcher.")

    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    print(f"[+] Got {WEBHOOK_URL=}")

    if not WEBHOOK_URL:
        print("[-] No webhook URL found. Please set one.")
        exit(1)

    URL = os.environ.get("RSS_FEED_URL")

    if not URL or "rpilocator" not in URL:
        print("[-] No rpilocator RSS feed URL found. Please set one.")
        exit(1)

    print(f"[+] Got {URL=}")

    while True:
        print("[+] Checking for new entries.")
        check_url()
        print("[+] Done. Sleeping for 5 minutes.")
        LAST_CHECKED = datetime.now()
        sleep(5 * 60)
