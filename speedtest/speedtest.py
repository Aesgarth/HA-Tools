import time
import subprocess
import argparse
import json
from paho.mqtt import publish

# Parse arguments
parser = argparse.ArgumentParser(description="SpeedTest Addon")
parser.add_argument("--ping-interval", type=int, default=5, help="Ping interval in minutes")
parser.add_argument("--speedtest-interval", type=int, default=30, help="Speed test interval in minutes")
parser.add_argument("--host", type=str, default="8.8.8.8", help="Host to ping")
args = parser.parse_args()

# MQTT configuration
MQTT_HOST = "homeassistant"
MQTT_PORT = 1883
MQTT_DISCOVERY_PREFIX = "homeassistant"
MQTT_TOPIC_CONNECTIVITY = "speedtest/internet_up"
MQTT_TOPIC_SPEED = "speedtest/speed_mbps"

def check_connectivity(host):
    """Ping the host and return True if reachable, otherwise False."""
    try:
        subprocess.check_call(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def run_speedtest():
    """Run speedtest-cli and return the download speed in Mbps."""
    try:
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if line.startswith("Download:"):
                return float(line.split()[1])  # Extract Mbps value
    except Exception:
        return 0.0

# Publish MQTT Discovery messages
def publish_discovery():
    # Connectivity entity
    connectivity_discovery = {
        "name": "Internet Connectivity",
        "state_topic": MQTT_TOPIC_CONNECTIVITY,
        "payload_on": "true",
        "payload_off": "false",
        "device_class": "connectivity",
        "unique_id": "speedtest_connectivity",
        "availability_topic": f"{MQTT_DISCOVERY_PREFIX}/availability",
    }
    publish.single(
        f"{MQTT_DISCOVERY_PREFIX}/binary_sensor/speedtest_connectivity/config",
        payload=json.dumps(connectivity_discovery),
        hostname=MQTT_HOST,
        port=MQTT_PORT,
    )

    # Speed entity
    speed_discovery = {
        "name": "Internet Speed",
        "state_topic": MQTT_TOPIC_SPEED,
        "unit_of_measurement": "Mbps",
        "device_class": "speed",
        "unique_id": "speedtest_speed",
        "availability_topic": f"{MQTT_DISCOVERY_PREFIX}/availability",
    }
    publish.single(
        f"{MQTT_DISCOVERY_PREFIX}/sensor/speedtest_speed/config",
        payload=json.dumps(speed_discovery),
        hostname=MQTT_HOST,
        port=MQTT_PORT,
    )

# Main loop
last_ping_time = time.time()
last_speedtest_time = time.time()

# Publish discovery at startup
publish_discovery()

while True:
    current_time = time.time()

    # Perform connectivity check
    if current_time - last_ping_time >= args.ping_interval * 60:
        is_connected = check_connectivity(args.host)
        publish.single(MQTT_TOPIC_CONNECTIVITY, payload="true" if is_connected else "false", hostname=MQTT_HOST, port=MQTT_PORT)
        print(f"Internet {'up' if is_connected else 'down'}")
        last_ping_time = current_time

    # Perform speed test
    if current_time - last_speedtest_time >= args.speedtest_interval * 60:
        download_speed = run_speedtest()
        publish.single(MQTT_TOPIC_SPEED, payload=download_speed, hostname=MQTT_HOST, port=MQTT_PORT)
        print(f"Download speed: {download_speed} Mbps")
        last_speedtest_time = current_time

    time.sleep(1)
