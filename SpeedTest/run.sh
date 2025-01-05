#!/bin/sh

CONFIG_PATH=/data/options.json

# Load configuration
PING_INTERVAL=$(jq --raw-output '.ping_interval' $CONFIG_PATH)
SPEEDTEST_INTERVAL=$(jq --raw-output '.speedtest_interval' $CONFIG_PATH)
HOST=$(jq --raw-output '.host' $CONFIG_PATH)

# Start the ping and speed test processes in the background
echo "Starting SpeedTest addon..."
python3 /app/speedtest.py --ping-interval $PING_INTERVAL --speedtest-interval $SPEEDTEST_INTERVAL --host $HOST
