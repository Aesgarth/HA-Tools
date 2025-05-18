#!/bin/sh

CONFIG_PATH=/data/options.json

# Load configuration for script arguments
PING_INTERVAL=$(jq --raw-output '.ping_interval // 5' $CONFIG_PATH)
SPEEDTEST_INTERVAL=$(jq --raw-output '.speedtest_interval // 30' $CONFIG_PATH)
PING_HOST=$(jq --raw-output '.host // "8.8.8.8"' $CONFIG_PATH)

# Load MQTT configuration for environment variables
export MQTT_HOST=$(jq --raw-output '.mqtt_host // "core-mosquitto"' $CONFIG_PATH)
export MQTT_PORT=$(jq --raw-output '.mqtt_port // 1883' $CONFIG_PATH)
export MQTT_USER=$(jq --raw-output '.mqtt_user // ""' $CONFIG_PATH)
export MQTT_PASSWORD=$(jq --raw-output '.mqtt_password // ""' $CONFIG_PATH)
export MQTT_DISCOVERY_PREFIX=$(jq --raw-output '.mqtt_discovery_prefix // "homeassistant"' $CONFIG_PATH)

# Ensure the data directory for results exists
mkdir -p /data

# Initialize results file with default values if it doesn't exist
RESULTS_FILE="/data/speedtest_results.json"
if [ ! -f "$RESULTS_FILE" ]; then
  echo '{
    "internet_status": "Initializing...",
    "last_test_time": "Never",
    "ping_ms": "N/A",
    "download_mbps": "N/A",
    "upload_mbps": "N/A"
  }' > "$RESULTS_FILE"
fi


# Start the SpeedTest script in the background
python3 /app/speedtest.py \
  --ping-interval "$PING_INTERVAL" \
  --speedtest-interval "$SPEEDTEST_INTERVAL" \
  --host "$PING_HOST" &

# Start the web server in the foreground
python3 /app/webserver.py