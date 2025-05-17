import json
import os
import time
import requests
from bs4 import BeautifulSoup
import re

DATA_FILE = "data/products.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=2)

def notify_discord(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if 200 <= response.status_code < 300:
        print("✅ Notification envoyée")
    else:
        print(f"❌ Erreur Discord : {response.status_code} - {response.text}")

def check_product(product):
    url = product["url"]
    max_price = float(product["max_price"])
    already_alerted = product.get("alerted", False)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"Erreur HTTP {r.status_code} pour {url}")
            return False, None

        soup = BeautifulSoup(r.text, "html.parser")
        page_text = soup.get_text(separator=' ', strip=True)

        stock_keywords = re.compile(r"(en stock|disponible|ajouter au panier|in stock|available)", re.IGNORECASE)
        if not stock_keywords.search(page_text):
            return False, None

        # Essayer d'extraire un prix approximatif
        price_match = re.search(r"(\d+[.,]?\d*)\s?€", page_text)
        if price_match:
            current_price = float(price_match.group(1).replace(",", "."))
            if current_price <= max_price:
                return True, current_price

        return True, None  # Stock dispo, mais pas de prix précis
    except Exception as e:
        print(f"Erreur scraping {url} : {e}")
        return False, None

def main_loop():
    while True:
        products = load_products()
        modified = False

        for product in products:
            in_stock, current_price = check_product(product)

            if in_stock and not product.get("alerted", False):
                message = f"🚨 Produit dispo : {product['url']}"
                if current_price:
                    message += f" — {current_price:.2f}€"

                notify_discord(message)
                product["alerted"] = True
                modified = True
            elif not in_stock:
                product["alerted"] = False  # reset si produit plus dispo
                modified = True

        if modified:
            save_products(products)

        print("🔁 Nouvelle vérification dans 60 sec")
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
