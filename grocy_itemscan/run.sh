#!/usr/bin/with-contenv bashio

# Log add-on startup
bashio::log.info "Starting Grocy Scanner Add-on"

# Retrieve options from configuration
API_KEY=$(bashio::config 'api_key')
GROCY_URL=$(bashio::config 'grocy_url')

# Log configuration
bashio::log.info "Using API Key: ${API_KEY}"
bashio::log.info "Grocy URL: ${GROCY_URL}"

# Start the service (replace this with actual code)
bashio::log.info "Running the Grocy Scanner service..."
exec python3 -m http.server 5000
