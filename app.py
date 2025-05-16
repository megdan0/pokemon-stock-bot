
from flask import Flask, request, render_template, redirect
import json
import os

app = Flask(__name__)

DATA_FILE = "data/products.json"

def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    with open(DATA_FILE, "w") as f:
        json.dump(products, f)

@app.route("/", methods=["GET", "POST"])
def index():
    products = load_products()
    if request.method == "POST":
        url = request.form.get("url")
        max_price = request.form.get("max_price")
        if url and max_price:
            products.append({"url": url, "max_price": float(max_price)})
            save_products(products)
        return redirect("/")
    return render_template("index.html", products=products)

@app.route("/delete/<int:index>")
def delete(index):
    products = load_products()
    if 0 <= index < len(products):
        products.pop(index)
        save_products(products)
    return redirect("/")

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)

