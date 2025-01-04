from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "default_api_key")
GROCY_URL = os.getenv("GROCY_URL", "http://your-default-grocy-instance")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Grocy Item Scanner is running!"})

@app.route("/scan", methods=["POST"])
def scan_barcode():
    barcode = request.json.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    try:
        # Query Open Food Facts
        logger.info(f"Querying Open Food Facts for barcode: {barcode}")
        response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
        response.raise_for_status()
        product_data = response.json()
        product_name = product_data.get("product", {}).get("product_name", "Unknown Product")

        # Add product to Grocy
        logger.info(f"Adding product to Grocy: {product_name}")
        add_to_grocy(product_name, barcode)
        return jsonify({"message": "Product added to Grocy", "product_name": product_name})

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during barcode processing: {e}")
        return jsonify({"error": str(e)}), 500

def add_to_grocy(name, barcode):
    headers = {"GROCY-API-KEY": GROCY_API_KEY, "Content-Type": "application/json"}
    data = {"name": name, "barcodes": [{"barcode": barcode}]}

    try:
        response = requests.post(f"{GROCY_URL}/api/objects/products", json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"Product added to Grocy successfully: {name}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to add product to Grocy: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080)
