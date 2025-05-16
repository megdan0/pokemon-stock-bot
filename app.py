from flask import Flask, request, render_template, redirect
import requests
import os

app = Flask(__name__)

# Stockage en mémoire simple
links = []

WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://discord.com/api/webhooks/..."  # Remplace en prod

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url and url not in links:
            links.append(url)
        return redirect("/")
    return render_template("index.html", links=links)

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(links):
        links.pop(index)
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
