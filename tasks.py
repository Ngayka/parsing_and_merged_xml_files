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

@shared_task
def merge_xml_files_task():
    if not os.path.isdir(FEED_DIR):
        os.makedirs(FEED_DIR, exist_ok=True)

    root = ET.Element("catalog")
    for url in XML_URLS:
        try:
            response = requests.get(url, timeout=60, headers={"User-Agent": "prom-feed-bot/1.0"})
            response.raise_for_status()

            tree = ET.parse(BytesIO(response.content))
            for element in tree.getroot():
                root.append(element)
        except Exception as e:
            print(f"[WARN] cannot load {url}: {e}")

    if not list(root):
        print("[ERROR] No valid source feed, nothing to write")
        return
    output_path = os.path.join(FEED_DIR, "merged_viatec.xml")
    ET.ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Wrote merged feed to {output_path}")
