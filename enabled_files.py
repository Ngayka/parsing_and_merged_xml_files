import xml.etree.ElementTree as ET
import requests
from io import BytesIO

def merge_xml_files(xml_urls, output_file):
    root = ET.Element("catalog")
    for url in xml_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            tree = ET.parse(BytesIO(response.content))
            for element in tree.getroot():
                root.append(element)
        except Exception as e:
            print(f"Exception while processing {url}: {e}")
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

xml_urls = [
    "https://viatec.ua/files/product_info_videonagliad_yml.xml",
    "https://viatec.ua/files/product_info_network_yml.xml",
    "https://viatec.ua/files/product_info_video-intercoms_yml.xml"
]

output_file = "merged_viatec.xml"

merge_xml_files(xml_urls, output_file)