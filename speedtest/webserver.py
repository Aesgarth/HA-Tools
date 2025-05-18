from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__, static_url_path="")
RESULTS_FILE = "/data/speedtest_results.json"

def get_default_results():
    return {
        "internet_status": "Unknown",
        "last_test_time": "Never",
        "ping_ms": "N/A",
        "download_mbps": "N/A",
        "upload_mbps": "N/A",
    }

@app.before_request
def handle_ingress():
    """Rewrite the path for Ingress."""
    # This function ensures that if the addon is accessed via an Ingress path like /addon_slug/
    # the Flask app still sees the routes as /
    # However, for this simple app, direct routing should work fine with Ingress.
    # Keeping it for compatibility or more complex routing scenarios.
    ingress_path = request.headers.get("X-Ingress-Path", "")
    if ingress_path:
        # If you have issues with static files or routes, you might need to adjust this.
        # For simple cases, routing directly from '/' often works with HA Ingress.
        pass # request.environ["PATH_INFO"] = request.path[len(ingress_path) :] - This line might be problematic for static files.


@app.route("/")
def index():
    results = get_default_results()
    try:
        with open(RESULTS_FILE, "r") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not load results file ({RESULTS_FILE}): {e}. Using defaults.")
        # The default results are already set
    
    # Ensure all keys are present
    for key, value in get_default_results().items():
        if key not in results:
            results[key] = value
            
    return render_template("index.html", results=results)

@app.route("/api/results")
def api_results():
    results = get_default_results()
    try:
        with open(RESULTS_FILE, "r") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Log error but return default data so the API endpoint still works
        print(f"API: Could not load results file ({RESULTS_FILE}): {e}. Using defaults.")

    for key, value in get_default_results().items():
        if key not in results:
            results[key] = value
            
    return jsonify(results)


if __name__ == "__main__":
    # Make sure the templates directory is correctly identified if running standalone
    # For addons, Home Assistant usually handles the working directory.
    # app.template_folder = 'templates' # Usually not needed when structured correctly
    
    port = int(os.environ.get("PORT", 3457)) # PORT is usually set by HA for Ingress
    print(f"Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False) # debug=False for production in addon