from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder='web_ui', static_url_path='')

# Configuration variables
GROCY_API_KEY = "your_default_key"
GROCY_URL = "http://your_default_url"
EXTERNAL_API = "https://ch.openfoodfacts.org/api/v0/product/"

@app.route('/scan', methods=['POST'])
def scan():
    barcode = request.json.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    try:
        external_response = requests.get(f"{EXTERNAL_API}{barcode}.json")
        external_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"External API error: {str(e)}"}), 500

    product_data = external_response.json()

    if "product" not in product_data or "product_name" not in product_data["product"]:
        return jsonify({"error": "Invalid product data from external API"}), 500

    try:
        grocy_response = requests.get(
            f"{GROCY_URL}/objects/products?query%5Bname%5D={product_data['product']['product_name']}",
            headers={"GROCY-API-KEY": GROCY_API_KEY}
        )
        grocy_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Grocy API error: {str(e)}"}), 500

    if grocy_response.status_code == 200 and grocy_response.json():
        return jsonify({"message": "Product exists in Grocy", "action": "add_inventory"}), 200

    return jsonify({"product": product_data}), 200

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found", "details": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8198)
