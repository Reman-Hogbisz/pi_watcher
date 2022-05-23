from xdrlib import ConversionError
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
USER_AGENT = "Hogbisz Pi Watcher"
FREQUENCY = 5  # In Minutes

LAST_CHECKED = datetime.now() - timedelta(hours=1)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def filter_entry(entry):
    time = datetime.fromtimestamp(mktime(entry['published_parsed']))
    return time > LAST_CHECKED


def check_url():
    feed_response = feedparser.parse(RSS_URL, agent=USER_AGENT)
    try:
        last_built = datetime.fromtimestamp(
            mktime(feed_response['feed']['updated_parsed']))
    except KeyError:
        eprint('[-] No updated_parsed key in feed')
        pp.pprint(feed_response)
        return

    if last_built < LAST_CHECKED:
        print("[-] No new posts")
        return

    try:
        entries = list(filter(filter_entry, feed_response['entries']))
    except KeyError:
        eprint('[-] No entries key in feed')
        pp.pprint(feed_response)
        return
    length_of_entries = len(entries)

    if length_of_entries > 0:
        print(f"[+] New posts found (found {length_of_entries})")

    for entry in entries:
        try:
            title = entry['title']
        except KeyError:
            eprint('[-] No title in entry')
            pp.pprint(entry)
            continue
        try:
            link = entry['link']
        except KeyError:
            eprint('[-] No link in entry')
            pp.pprint(entry)
            continue
        print(f"\t[+] Got new entry: {title}\n\t\t{link}")
        requests.post(WEBHOOK_URL, json={
            "content": f"{title}\n{link}"})
        sleep(0.25)


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

    USER_AGENT_OPTION = os.environ.get("USER_AGENT")

    if USER_AGENT_OPTION:
        USER_AGENT = USER_AGENT_OPTION

    FREQUENCY = os.environ.get("FREQUENCY")

    if not FREQUENCY:
        print("[-] No frequency environment variabel found. Defaulting to 5 minutes.")
        FREQUENCY = 5
    else:
        print(
            "[+] Found FREQUENCY environment variable. Attempting to convert it to a float.")
        try:
            FREQUENCY = float(FREQUENCY)
            print(f"[+] Converted {FREQUENCY} to float.")
            if FREQUENCY <= 0:
                print(f"{FREQUENCY} is an invalid frequency! Defaulting to 5")
                FREQUENCY = 5
        except ConversionError:
            print(
                f"[-] Failed to convert {FREQUENCY} to a floating point number! Defaulting to 5 minutes.")
            FREQUENCY = 5

    while True:
        print("[+] Checking for new entries.")
        check_url()
        print(f"[+] Done. Sleeping for {FREQUENCY} minutes.")
        LAST_CHECKED = datetime.now()
        sleep(FREQUENCY * 60)
