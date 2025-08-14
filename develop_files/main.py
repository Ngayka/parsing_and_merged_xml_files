import requests
import xmltodict
import sqlite3

url = "https://viatec.ua/files/product_info_videonagliad_yml.xml"
response = requests.get(url)
response.raise_for_status()

data = xmltodict.parse(response.text)

categories = data["shop"]["categories"]["category"]
offers = data["shop"]["offers"]["offer"]

conn = sqlite3.connect("viatec.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT,
    price REAL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")

for cat in categories:
    cursor.execute(
        "INSERT OR REPLACE INTO categories (id, name) VALUES (?, ?)",
        (int(cat["@id"]), cat["#text"])
    )

for offer in offers:
    price = offer.get("price")
    try:
        price = float(price) if price is not None else None
    except ValueError:
        price = None

    category_id = offer.get("categoryId")
    try:
        category_id = int(category_id) if category_id is not None else None
    except ValueError:
        category_id = None

    cursor.execute(
        "INSERT OR REPLACE INTO offers (code, name, price, category_id) VALUES (?, ?, ?, ?)",
        (
            offer["@id"],
            offer.get("name"),
            price,
            category_id
        )
    )

conn.commit()
conn.close()

print("Data has been saved to viatec.db")
