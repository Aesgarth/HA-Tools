#!/bin/bash
# Start the API
python3 api/app.py &

# Serve the web UI
cd web_ui && python3 -m http.server 8099
