from flask import Flask, render_template, jsonify, request
import requests
import os

app = Flask(__name__, template_folder="/app/templates")

# Configuration
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "default_api_key")
GROCY_URL = os.getenv("GROCY_URL", "http://your-default-grocy-instance")

# Log environment variables
@app.before_request
def log_requests():
    print(f"Request Path: {request.path}")
    print(f"Request Method: {request.method}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.data}")

# Remove Ingress Prefix
@app.before_request
def remove_ingress_prefix():
    print(f"Original Request Path: {request.path}")
    if request.path.startswith("/api/hassio_ingress"):
        # Strip ingress prefix
        request.environ['PATH_INFO'] = request.path[len("/api/hassio_ingress"):]
        print(f"Modified Request Path: {request.environ['PATH_INFO']}")

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Scan Barcode Endpoint
@app.route("/scan", methods=["POST"])
def scan_barcode():
    return jsonify({"message": "Scan endpoint is reachable!"})
    # Ensure Content-Type is JSON
    if not request.is_json:
        return jsonify({"error": "Invalid Content-Type. Expected application/json."}), 415

    try:
        # Extract barcode from JSON payload
        data = request.get_json()
        barcode = data.get("barcode")
        if not barcode:
            return jsonify({"error": "No barcode provided"}), 400

        # Query Open Food Facts
        response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
        response.raise_for_status()

        product_data = response.json()
        product_name = product_data.get("product", {}).get("product_name", "Unknown Product")

        # Add product to Grocy
        add_to_grocy(product_name, barcode)

        return jsonify({"message": "Product added", "product_name": product_name})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error querying product database: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Add Product to Grocy
def add_to_grocy(name, barcode):
    try:
        headers = {"GROCY-API-KEY": GROCY_API_KEY, "Content-Type": "application/json"}
        data = {"name": name, "barcodes": [{"barcode": barcode}]}
        response = requests.post(f"{GROCY_URL}/api/objects/products", json=data, headers=headers)
        if response.status_code != 200:
            print(f"Failed to add product to Grocy: {response.content}")
    except Exception as e:
        print(f"Error adding to Grocy: {str(e)}")

# Start the Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
