import requests
import feedparser
import os
import sys
from datetime import datetime, timedelta
from time import sleep, mktime
import pprint

pp = pprint.PrettyPrinter(indent=4)

RSS_URL = None
WEBHOOK_URL = None

LAST_CHECKED = datetime.now() - timedelta(hours=1)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def filter_entry(entry):
    time = datetime.fromtimestamp(mktime(entry['published_parsed']))
    return time > LAST_CHECKED


def check_url():
    feed_response = feedparser.parse(RSS_URL)
    try:
        last_built = datetime.fromtimestamp(
            mktime(feed_response['feed']['updated_parsed']))
    except KeyError:
        eprint('No updated_parsed key in feed')
        pp.print(feed_response)
        return

    if last_built < LAST_CHECKED:
        print("[-] No new posts")
        return

    try:
        entries = list(filter(filter_entry, feed_response['entries']))
    except KeyError:
        eprint('No entries key in feed')
        pp.print(feed_response)
        return
    length_of_entries = len(entries)

    if length_of_entries > 0:
        print(f"[+] New posts found (found {length_of_entries})")

    for entry in entries:
        try:
            title = entry['title']
        except KeyError:
            eprint('No title in entry')
            pp.print(entry)
            continue
        try:
            link = entry['link']
        except KeyError:
            eprint('No link in entry')
            pp.print(entry)
            continue
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

    RSS_URL = os.environ.get("RSS_URL")

    if not RSS_URL or "rpilocator" not in RSS_URL:
        print("[-] No rpilocator RSS feed URL found. Please set one.")
        exit(1)

    print(f"[+] Got {RSS_URL=}")

    while True:
        print("[+] Checking for new entries.")
        check_url()
        print("[+] Done. Sleeping for 5 minutes.")
        LAST_CHECKED = datetime.now()
        sleep(5 * 60)
