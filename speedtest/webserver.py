from flask import Flask, render_template, request
import os

app = Flask(__name__, static_url_path="")

# Sample results for demonstration
results = {
    "internet_status": "Up",
    "last_ping_time": "2025-01-05 20:00:00",
    "download_speed": "85.6 Mbps",
    "upload_speed": "23.4 Mbps",
}

@app.before_request
def handle_ingress():
    """Rewrite the path for Ingress."""
    ingress_path = os.getenv("INGRESS_ENTRY", "/")
    if request.path.startswith(ingress_path):
        request.environ["PATH_INFO"] = request.path[len(ingress_path) :]

@app.route("/")
def index():
    return render_template("index.html", results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3457))
    app.run(host="0.0.0.0", port=port)
