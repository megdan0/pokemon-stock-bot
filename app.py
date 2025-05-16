from flask import Flask, request, render_template, redirect
import json
import os
import requests

app = Flask(__name__)

DATA_FILE = "data/products.json"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1372700039163547679/Na9vuRQenw8Es5RrACzED7HJRjPknKs5FCRV6vVflkCWh7bxByshKbQBejhpdapuVFAK"

def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=2)

def send_discord_notification(message):
    # code pour envoyer une notification sur Discord
    pass

def notify_discord(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification envoyée sur Discord")
    else:
        print(f"Erreur notification Discord : {response.status_code} - {response.text}")

def check_product_availability(product):
    url = product["url"]
    max_price = product["max_price"]
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            page_content = response.text.lower()
            # Exemple très simple : on considère que le produit est dispo si "en stock" est présent dans la page
            if "en stock" in page_content or "disponible" in page_content:
                # Ici on ne fait pas de parsing prix précis, juste un exemple d'envoi de notif
                notify_discord(f"Produit disponible à vérifier : {url} (prix max: {max_price}€)")
                return True
            else:
                print(f"Produit pas dispo pour {url}")
        else:
            print(f"Erreur HTTP {response.status_code} pour {url}")
    except Exception as e:
        print(f"Erreur lors de la vérification de {url}: {e}")
    return False

@app.route("/", methods=["GET", "POST"])
def index():
    url = None
    max_price = None
    products = load_products()
    if request.method == "POST":
        url = request.form.get("url")
        max_price = request.form.get("max_price")
    if url and max_price:
        products.append({"url": url, "max_price": float(max_price)})
        save_products(products)
        send_discord_notification(f"Nouveau produit ajouté : {url} avec un prix max de {max_price}€")

        return redirect("/")
    return render_template("index.html", products=products)

@app.route("/delete/<int:index>")
def delete(index):
    products = load_products()
    if 0 <= index < len(products):
        products.pop(index)
        save_products(products)
    return redirect("/")

@app.route("/check")
def check_all():
    products = load_products()
    dispo_products = []
    for product in products:
        if check_product_availability(product):
            dispo_products.append(product["url"])
    if dispo_products:
        return f"Produits dispo: <br>" + "<br>".join(dispo_products)
    else:
        return "Aucun produit disponible pour le moment."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
