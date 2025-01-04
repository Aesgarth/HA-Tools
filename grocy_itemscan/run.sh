#!/usr/bin/with-contenv bashio

# Log startup
bashio::log.info "Starting Grocy Item Scanner Add-on"

# Retrieve options from the configuration
API_KEY=$(bashio::config 'api_key')
GROCY_URL=$(bashio::config 'grocy_url')

# Log configuration
bashio::log.info "Using API Key: ${API_KEY}"
bashio::log.info "Grocy URL: ${GROCY_URL}"

# Start the service (replace this with your application logic)
bashio::log.info "Running service..."
exec python3 -m http.server 5000
