from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GROCY_API_KEY = "your_default_key"
GROCY_URL = "http://your_default_url"
EXTERNAL_API = "https://ch.openfoodfacts.org/api/v0/product/"

@app.route('/scan', methods=['POST'])
def scan():
    barcode = request.json.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    # Look up product in external API
    external_response = requests.get(f"{EXTERNAL_API}{barcode}.json")
    if external_response.status_code != 200:
        return jsonify({"error": "External API error"}), 500

    product_data = external_response.json()

    # Check Grocy
    grocy_response = requests.get(
        f"{GROCY_URL}/objects/products?query%5Bname%5D={product_data['product']['product_name']}",
        headers={"GROCY-API-KEY": GROCY_API_KEY}
    )

    if grocy_response.status_code == 200 and grocy_response.json():
        return jsonify({"message": "Product exists in Grocy", "action": "add_inventory"}), 200

    # Else, return details for new product creation
    return jsonify({"product": product_data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8199)
