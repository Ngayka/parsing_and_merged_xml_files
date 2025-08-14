import os
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from celery import shared_task
import requests

FEED_DIR = os.getenv('FEED_DIR', "/var/www/prom-feed") #передивитися посилання на промі
FEED_NAME = os.getenv('FEED_NAME', "merged_viatec.xml")
OUTPUT_PATH = os.path.join(FEED_DIR, FEED_NAME)

XML_URLS = [
        "https://viatec.ua/files/product_info_videonagliad_yml.xml",
        "https://viatec.ua/files/product_info_network_yml.xml",
        "https://viatec.ua/files/product_info_video-intercoms_yml.xml"
    ]

def fetch_tree(url: str):
    response = requests.get(url, timeout=60, headers={"User-Agent": "prom-feed-bot/1.0"})
    response.raise_for_status()
    tree = ET.parse(BytesIO(response.content))


@shared_task
def merge_xml_files_task():
    if not os.path.isdir(FEED_DIR):
        os.makedirs(FEED_DIR, exist_ok=True)

    base_tree = None
    base_root = None
    base_offers = None

    for idx, url in enumerate(XML_URLS):
        try:
            tree = fetch_tree(url)

        except Exception as e:
            print(f"[WARN] cannot load {url}: {e}")
            continue

        root = tree.getroot()
        shop = root.find("shop")
        offers = shop.find("offers") if shop is not None else None

        if shop is None or offers is None:
            print(f"[WARN] {url} has no <shop>/<offers>, skipping")
            continue

        if base_tree is None:
            base_tree = tree
            base_offers = offers
            base_root = shop
            print(f"Using {url} as base")

        else:
            added = 0
            existing_ids = {o.get("id") for o in base_offers.findall("offer") if o.get("id")}
            for offer in offers.findall("offer"):
                oid = offer.get("id")
                if oid and oid in existing_ids:
                    continue
                base_offers.append(offer)
                added += 1
            print(f"Added {added} new offer from {url}")

    if base_tree is None:
        print(f"[ERROR] No valid sourse feeds, nothing to write")
        return
    with tempfile.TemporaryFile("wb", delete=False, dir=FEED_DIR) as tmp:
        tmp.path = tmp.name
        base_tree.write(tmp, encoding="utf-8", xml_declaration=True)

    os.replace(tmp.path, OUTPUT_PATH)
    print(f"[OK] Wrote merged feed to {OUTPUT_PATH}")