from flask import Flask, render_template
import os

app = Flask(__name__)

# Sample results for demonstration
# Replace these with actual test results from speedtest.py
results = {
    "internet_status": "Up",
    "last_ping_time": "2025-01-05 20:00:00",
    "download_speed": "85.6 Mbps",
    "upload_speed": "23.4 Mbps",
}

@app.route("/")
def index():
    return render_template("index.html", results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3456))
    app.run(host="0.0.0.0", port=port)