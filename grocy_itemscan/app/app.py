from flask import Flask, render_template, jsonify, request
import requests
import os

app = Flask(__name__, template_folder="/app/templates")

# Configuration
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "default_api_key")
GROCY_URL = os.getenv("GROCY_URL", "http://your-default-grocy-instance")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan_barcode():
    barcode = request.json.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    # Query Open Food Facts as an example
    response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
    if response.status_code != 200:
        return jsonify({"error": "Failed to query Open Food Facts"}), 500

    product_data = response.json()
    product_name = product_data.get("product", {}).get("product_name", "Unknown Product")

    # Add product to Grocy
    add_to_grocy(product_name, barcode)
    return jsonify({"message": "Product added to Grocy", "product_name": product_name})

def add_to_grocy(name, barcode):
    headers = {"GROCY-API-KEY": GROCY_API_KEY, "Content-Type": "application/json"}
    data = {"name": name, "barcodes": [{"barcode": barcode}]}
    response = requests.post(f"{GROCY_URL}/api/objects/products", json=data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to add product to Grocy: {response.content}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080)
