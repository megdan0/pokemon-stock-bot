
import requests
from bs4 import BeautifulSoup
import json
import time
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://discord.com/api/webhooks/1372700039163547679/Na9vuRQenw8Es5RrACzED7HJRjPknKs5FCRV6vVflkCWh7bxByshKbQBejhpdapuVFAK"

DATA_FILE = "data/products.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

notified = {}

def load_products():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def send_discord_alert(product_url, price):
    message = {
        "content": f"🛒 Produit dispo à {price:.2f} € : {product_url}"
    }
    requests.post(WEBHOOK_URL, json=message)

def check_product(product):
    url = product["url"]
    max_price = product["max_price"]
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        price_tag = soup.select_one("#priceblock_ourprice, #priceblock_dealprice")
        if not price_tag:
            return

        price_text = price_tag.text.strip().replace("€", "").replace(",", ".")
        price = float("".join(c for c in price_text if c.isdigit() or c == "."))

        if price <= max_price:
            if url not in notified:
                send_discord_alert(url, price)
                notified[url] = True
        else:
            notified.pop(url, None)
    except Exception as e:
        print(f"Erreur pour {url} : {e}")

def run():
    while True:
        products = load_products()
        for product in products:
            check_product(product)
        time.sleep(30)

if __name__ == "__main__":
    run()
