#!/usr/bin/with-contenv bashio

# Log startup
bashio::log.info "Starting Grocy Item Scanner Add-on"

# Retrieve options from the configuration
API_KEY=$(bashio::config 'api_key')
GROCY_URL=$(bashio::config 'grocy_url')

# Log configuration
bashio::log.info "Using API Key: ${API_KEY}"
bashio::log.info "Grocy URL: ${GROCY_URL}"

# Start the Flask application
exec python3 /app/app.py

# Start the service (replace this with your application logic)
bashio::log.info "Starting HTTP server on port 5080..."
python3 -m http.server 5080 
