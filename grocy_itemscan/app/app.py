from flask import Flask, render_template, jsonify, request
import requests
import os

app = Flask(__name__, template_folder="/app/templates")

# Configuration
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "default_api_key")
GROCY_URL = os.getenv("GROCY_URL", "http://your-default-grocy-instance")

# Log the configuration once on the first request
first_request_logged = False

@app.before_request
def log_configuration():
    global first_request_logged
    if not first_request_logged:
        print(f"API Key: {GROCY_API_KEY}")
        print(f"Grocy URL: {GROCY_URL}")
        first_request_logged = True
@app.before_request
def log_requests():
    print(f"Request Path: {request.path}")
    print(f"Request Method: {request.method}")
    print(f"Request Body: {request.json if request.json else 'No Body'}")


@app.before_request
def remove_ingress_prefix():
    """Strip /api/hassio_ingress prefix for Ingress requests."""
    if request.path.startswith("/api/hassio_ingress"):
        request.environ['PATH_INFO'] = request.path[len("/api/hassio_ingress"):]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan_barcode():
    try:
        barcode = request.json.get("barcode")
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

def add_to_grocy(name, barcode):
    headers = {"GROCY-API-KEY": GROCY_API_KEY, "Content-Type": "application/json"}
    data = {"name": name, "barcodes": [{"barcode": barcode}]}
    response = requests.post(f"{GROCY_URL}/api/objects/products", json=data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to add product to Grocy: {response.content}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
