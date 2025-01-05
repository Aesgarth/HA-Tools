from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder="web_ui", static_url_path="")

# Configuration variables
GROCY_API_KEY = "your_default_key"
GROCY_URL = "http://your_default_url"
EXTERNAL_API = "https://ch.openfoodfacts.org/api/v0/product/"

@app.route('/')
def serve_index():
    """
    Serve the main index.html for the web UI.
    """
    return send_from_directory(app.static_folder, "index.html")

@app.route('/<path:path>')
def serve_static(path):
    """
    Serve static files like CSS, JavaScript, and favicon.
    """
    return send_from_directory(app.static_folder, path)

@app.route('/favicon.ico')
def favicon():
    """
    Handle requests for favicon.ico.
    """
    return ('', 204)  # Return "No Content" to suppress errors

@app.route('/scan', methods=['POST'])
def scan():
    """
    Endpoint to scan a barcode, lookup product details, and integrate with Grocy.
    """
    barcode = request.json.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    try:
        # Look up product in external API
        external_response = requests.get(f"{EXTERNAL_API}{barcode}.json")
        external_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"External API error: {str(e)}"}), 500

    product_data = external_response.json()

    # Validate external API response structure
    if "product" not in product_data or "product_name" not in product_data["product"]:
        return jsonify({"error": "Invalid product data from external API"}), 500

    try:
        # Check Grocy for existing product
        grocy_response = requests.get(
            f"{GROCY_URL}/objects/products?query%5Bname%5D={product_data['product']['product_name']}",
            headers={"GROCY-API-KEY": GROCY_API_KEY}
        )
        grocy_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Grocy API error: {str(e)}"}), 500

    # Determine if product exists
    if grocy_response.status_code == 200 and grocy_response.json():
        return jsonify({"message": "Product exists in Grocy", "action": "add_inventory"}), 200

    # Return details for new product creation
    return jsonify({"product": product_data}), 200

@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors for better debugging.
    """
    return jsonify({"error": "Page not found", "details": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8198)
