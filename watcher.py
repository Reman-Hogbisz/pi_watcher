from random import randint
from xdrlib import ConversionError
import requests
import feedparser
import os
import sys
from datetime import datetime, timedelta
from time import sleep, mktime, strftime
import pprint
from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)

RSS_URL = None
WEBHOOK_URL = None
USER_AGENT = "Hogbisz Pi Watcher"
FREQUENCY = 5  # In Minutes
DEBUG = False

LAST_CHECKED = datetime.now() - timedelta(minutes=20)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def filter_entry(entry):
    try:
        time = datetime.fromtimestamp(mktime(entry['published_parsed']))
        return time > LAST_CHECKED
    except KeyError:
        eprint('[-] No published_parsed key in entry')
        pp.pprint(entry)
        return False


def check_url():
    global LAST_CHECKED
    feed_response = feedparser.parse(RSS_URL, agent=USER_AGENT)
    if DEBUG:
        pp.pprint(feed_response)
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

    embeds = []

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
        try:
            time = entry['published_parsed']
        except KeyError:
            eprint('[-] No published in entry')
            pp.pprint(entry)
            continue
        print(f"\t[+] Got new entry: {title}\n\t\t{link}\n\t\t{time}")
        embeds.append({
            "fields": [
                {
                    "name": "Title",
                    "value": title
                },
                {
                    "name": "Link",
                    "value": link
                }
            ],
            "color": randint(0, 0xffffff),
            "timestamp": strftime('%Y-%m-%dT%H:%M:%SZ', time)
        })
    if DEBUG:
        pp.pprint(embeds)
    requests.post(WEBHOOK_URL, json={
        "embeds": embeds
    })
    LAST_CHECKED = datetime.now()


if __name__ == "__main__":
    load_dotenv()
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
        print(f"[+] Got {USER_AGENT_OPTION=}")
    else:
        print("[-] No user agent found. Using default. ('Hogbisz Pi Watcher')")

    FREQUENCY = os.environ.get("FREQUENCY")

    if not FREQUENCY:
        print("[-] No frequency environment variable found. Defaulting to 5 minutes.")
        FREQUENCY = 5
    else:
        print(
            "[+] Found FREQUENCY environment variable. Attempting to convert it to a float.")
        try:
            FREQUENCY = float(FREQUENCY)
            print(f"[+] Converted {FREQUENCY} to float.")
            if FREQUENCY <= 0:
                print(
                    f"[-] {FREQUENCY} is an invalid frequency! Defaulting to 5 minutes.")
                FREQUENCY = 5
        except ConversionError:
            print(
                f"[-] Failed to convert {FREQUENCY} to a floating point number! Defaulting to 5 minutes.")
            FREQUENCY = 5

    while True:
        print("[+] Checking for new entries.")
        check_url()
        print(f"[+] Done. Sleeping for {FREQUENCY} minutes.")
        sleep(FREQUENCY * 60)
