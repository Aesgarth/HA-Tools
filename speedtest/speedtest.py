import time
import subprocess
import argparse
import json
import os
from paho.mqtt import publish, client as mqtt_client
from datetime import datetime

# --- Configuration ---
RESULTS_FILE = "/data/speedtest_results.json"

# --- Helper Functions ---
def get_mqtt_config():
    """Gets MQTT configuration from environment variables."""
    config = {
        "host": os.getenv("MQTT_HOST", "localhost"),
        "port": int(os.getenv("MQTT_PORT", 1883)),
        "username": os.getenv("MQTT_USER", None),
        "password": os.getenv("MQTT_PASSWORD", None),
        "discovery_prefix": os.getenv("MQTT_DISCOVERY_PREFIX", "homeassistant"),
    }
    if config["username"] == "" or config["username"] is None:
        config["auth"] = None
    else:
        config["auth"] = {"username": config["username"], "password": config["password"]}
    return config

def update_results_file(data):
    """Saves the latest results to the JSON file."""
    try:
        with open(RESULTS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Results updated: {data}")
    except IOError as e:
        print(f"Error writing results to file: {e}")

def load_results_file():
    """Loads results from the JSON file."""
    try:
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError): # Handle file not found or corrupt JSON
        return {
            "internet_status": "Unknown",
            "last_test_time": "Never",
            "ping_ms": "N/A",
            "download_mbps": "N/A",
            "upload_mbps": "N/A",
        }

def check_connectivity(host_to_ping):
    """Ping the host and return True if reachable, otherwise False."""
    try:
        subprocess.check_call(["ping", "-c", "1", "-W", "1", host_to_ping], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError: # ping command not found
        print("Error: 'ping' command not found. Cannot check connectivity.")
        return False


def run_speedtest_cli():
    """Run speedtest-cli and return ping, download, and upload speeds."""
    ping = download = upload = 0.0
    try:
        print("Running speedtest-cli...")
        result = subprocess.run(["speedtest-cli", "--simple", "--timeout", "60"], capture_output=True, text=True, check=True)
        print(f"Speedtest-cli output:\n{result.stdout}")
        for line in result.stdout.splitlines():
            if line.startswith("Ping:"):
                ping = float(line.split(":")[1].strip().split(" ")[0])
            elif line.startswith("Download:"):
                download = float(line.split(":")[1].strip().split(" ")[0])
            elif line.startswith("Upload:"):
                upload = float(line.split(":")[1].strip().split(" ")[0])
        print(f"Speedtest successful: Ping={ping}ms, Download={download}Mbps, Upload={upload}Mbps")
        return ping, download, upload
    except subprocess.CalledProcessError as e:
        print(f"Error running speedtest-cli: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return 0.0, 0.0, 0.0
    except FileNotFoundError:
        print("Error: 'speedtest-cli' command not found. Please ensure it's installed and in PATH.")
        return 0.0, 0.0, 0.0
    except Exception as e:
        print(f"An unexpected error occurred during speedtest: {e}")
        return 0.0, 0.0, 0.0

def publish_mqtt_message(mqtt_config, topic, payload_value, retain=False):
    """Publishes a single MQTT message."""
    try:
        publish.single(
            topic,
            payload=str(payload_value),
            hostname=mqtt_config["host"],
            port=mqtt_config["port"],
            auth=mqtt_config["auth"],
            retain=retain,
            protocol=mqtt_client.MQTTv311 # Specify MQTT protocol version
        )
        print(f"MQTT Published: Topic='{topic}', Payload='{payload_value}'")
    except Exception as e:
        print(f"MQTT Publish Error to {topic}: {e}")

def publish_mqtt_discovery(mqtt_config, current_results):
    """Publish MQTT Discovery messages for all sensors."""
    device_info = {
        "identifiers": ["ha_addon_speedtest_monitor"],
        "name": "SpeedTest Monitor",
        "manufacturer": "Home Assistant Addon",
        "model": "SpeedTest",
        "sw_version": "1.1.0" # Match config.yaml version
    }
    
    availability_topic = f"{mqtt_config['discovery_prefix']}/sensor/speedtest_monitor/availability"
    
    # Base payload for availability
    base_availability = [{"topic": availability_topic, "payload_available": "online", "payload_not_available": "offline"}]


    sensors = [
        {
            "component": "binary_sensor",
            "id": "connectivity",
            "name": "Internet Connectivity",
            "state_topic": f"{mqtt_config['discovery_prefix']}/binary_sensor/speedtest_connectivity/state",
            "payload_on": "online",
            "payload_off": "offline",
            "device_class": "connectivity",
            "availability": base_availability
        },
        {
            "component": "sensor",
            "id": "ping",
            "name": "Internet Ping",
            "state_topic": f"{mqtt_config['discovery_prefix']}/sensor/speedtest_ping/state",
            "unit_of_measurement": "ms",
            "icon": "mdi:timer-sand",
            "value_template": "{{ value | float(0) }}",
            "availability": base_availability
        },
        {
            "component": "sensor",
            "id": "download",
            "name": "Internet Download Speed",
            "state_topic": f"{mqtt_config['discovery_prefix']}/sensor/speedtest_download/state",
            "unit_of_measurement": "Mbps",
            "icon": "mdi:download-network",
            "value_template": "{{ value | float(0) }}",
            "availability": base_availability
        },
        {
            "component": "sensor",
            "id": "upload",
            "name": "Internet Upload Speed",
            "state_topic": f"{mqtt_config['discovery_prefix']}/sensor/speedtest_upload/state",
            "unit_of_measurement": "Mbps",
            "icon": "mdi:upload-network",
            "value_template": "{{ value | float(0) }}",
            "availability": base_availability
        }
    ]

    for sensor in sensors:
        discovery_topic = f"{mqtt_config['discovery_prefix']}/{sensor['component']}/speedtest_{sensor['id']}/config"
        payload = {
            "name": sensor["name"],
            "state_topic": sensor["state_topic"],
            "unique_id": f"speedtest_{sensor['id']}_sensor",
            "device": device_info,
            "availability": sensor.get("availability", base_availability), # Use default if not specified
        }
        if "unit_of_measurement" in sensor:
            payload["unit_of_measurement"] = sensor["unit_of_measurement"]
        if "device_class" in sensor:
            payload["device_class"] = sensor["device_class"]
        if "icon" in sensor:
            payload["icon"] = sensor["icon"]
        if "payload_on" in sensor: # For binary_sensor
            payload["payload_on"] = sensor["payload_on"]
            payload["payload_off"] = sensor["payload_off"]
        if "value_template" in sensor:
            payload["value_template"] = sensor["value_template"]

        publish_mqtt_message(mqtt_config, discovery_topic, json.dumps(payload), retain=True)
    
    # Publish initial availability
    publish_mqtt_message(mqtt_config, availability_topic, "online", retain=True)
    print("MQTT Discovery messages published.")


def main():
    parser = argparse.ArgumentParser(description="SpeedTest Addon Script")
    parser.add_argument("--ping-interval", type=int, default=5, help="Ping interval in minutes")
    parser.add_argument("--speedtest-interval", type=int, default=30, help="Speed test interval in minutes")
    parser.add_argument("--host", type=str, default="8.8.8.8", help="Host to ping for connectivity check")
    args = parser.parse_args()

    mqtt_cfg = get_mqtt_config()
    current_data = load_results_file() # Load initial data or defaults

    print(f"Starting SpeedTest Monitor: Ping Interval={args.ping_interval}m, SpeedTest Interval={args.speedtest_interval}m, Ping Host={args.host}")
    print(f"MQTT Config: Host={mqtt_cfg['host']}, Port={mqtt_cfg['port']}, User={mqtt_cfg['username']}, Discovery Prefix={mqtt_cfg['discovery_prefix']}")

    # Publish discovery on startup
    publish_mqtt_discovery(mqtt_cfg, current_data)

    # Publish initial state from file (or defaults)
    publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/binary_sensor/speedtest_connectivity/state", "online" if current_data.get("internet_status") == "Up" else "offline")
    publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_ping/state", current_data.get("ping_ms", 0))
    publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_download/state", current_data.get("download_mbps", 0))
    publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_upload/state", current_data.get("upload_mbps", 0))


    last_ping_check_time = 0 # Force immediate check on first run
    last_speedtest_run_time = 0 # Force immediate check on first run

    # Initial status update for the JSON file
    current_data["internet_status"] = "Initializing..."
    update_results_file(current_data)


    while True:
        current_time = time.time()

        # Perform connectivity check
        if current_time - last_ping_check_time >= args.ping_interval * 60:
            print("Performing connectivity check...")
            is_connected = check_connectivity(args.host)
            current_data["internet_status"] = "Up" if is_connected else "Down"
            current_data["last_test_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Update time on ping
            
            # Publish connectivity status to MQTT
            publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/binary_sensor/speedtest_connectivity/state", "online" if is_connected else "offline")
            
            # If connection is down, report 0 for speeds and N/A for ping if not running full test
            if not is_connected:
                current_data["ping_ms"] = "N/A" # Or some other indicator
                current_data["download_mbps"] = 0.0
                current_data["upload_mbps"] = 0.0
                # Publish 0 speeds if down
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_ping/state", 0) # Ping 0 could mean down
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_download/state", 0)
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_upload/state", 0)

            update_results_file(current_data)
            print(f"Connectivity check: Internet is {'up' if is_connected else 'down'}")
            last_ping_check_time = current_time

        # Perform speed test
        if current_time - last_speedtest_run_time >= args.speedtest_interval * 60:
            print("Performing speed test...")
            if check_connectivity(args.host): # Only run speedtest if connected
                current_data["internet_status"] = "Up" # Confirm status
                ping_ms, download_mbps, upload_mbps = run_speedtest_cli()
                current_data["ping_ms"] = round(ping_ms, 2) if ping_ms is not None else "N/A"
                current_data["download_mbps"] = round(download_mbps, 2) if download_mbps is not None else "N/A"
                current_data["upload_mbps"] = round(upload_mbps, 2) if upload_mbps is not None else "N/A"
                
                # Publish to MQTT
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/binary_sensor/speedtest_connectivity/state", "online")
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_ping/state", current_data["ping_ms"])
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_download/state", current_data["download_mbps"])
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_upload/state", current_data["upload_mbps"])
                print(f"Speed test results: Ping={current_data['ping_ms']}ms, Download={current_data['download_mbps']}Mbps, Upload={current_data['upload_mbps']}Mbps")
            else:
                current_data["internet_status"] = "Down"
                current_data["ping_ms"] = "N/A"
                current_data["download_mbps"] = 0.0
                current_data["upload_mbps"] = 0.0
                # Publish MQTT status for down
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/binary_sensor/speedtest_connectivity/state", "offline")
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_ping/state", 0)
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_download/state", 0)
                publish_mqtt_message(mqtt_cfg, f"{mqtt_cfg['discovery_prefix']}/sensor/speedtest_upload/state", 0)
                print("Internet is down. Skipping speed test.")

            current_data["last_test_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_results_file(current_data)
            last_speedtest_run_time = current_time
            # Ensure discovery is published periodically, or if MQTT connection might have dropped
            publish_mqtt_discovery(mqtt_cfg, current_data)


        time.sleep(max(1, min(args.ping_interval * 60, args.speedtest_interval * 60) // 10)) # Sleep for a fraction of the shortest interval, but at least 1s

if __name__ == "__main__":
    main()