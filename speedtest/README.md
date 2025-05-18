# SpeedTest Monitor Add-on for Home Assistant

This Home Assistant add-on periodically checks your internet connectivity and measures your internet speed (ping, download, and upload). Results are published via MQTT for integration with Home Assistant sensors and are also displayed on a local web UI accessible via Ingress.

## Features

-   **Periodic Speed Tests:** Automatically runs speed tests at configurable intervals using `speedtest-cli`.
-   **Connectivity Checks:** Regularly pings a specified host to determine internet status.
-   **MQTT Integration:**
    -   Publishes internet status (up/down).
    -   Publishes ping (ms), download speed (Mbps), and upload speed (Mbps).
    -   Supports MQTT discovery for automatic sensor creation in Home Assistant.
-   **Web UI (Ingress):** Displays the latest test results directly in the Home Assistant interface.
-   **Configurable:**
    -   Set intervals for ping checks and full speed tests.
    -   Configure the host for ping checks.
    -   Configure all necessary MQTT parameters (host, port, user, password, discovery prefix).

## Installation

1.  **Add Repository:**
    * Go to your Home Assistant Supervisor panel -> Add-on Store.
    * Click the 3 dots in the top right and select "Repositories".
    * Add the URL of your repository (e.g., `https://github.com/your-username/your-repo-name`) and click "Add".
2.  **Install Add-on:**
    * Find "SpeedTest Monitor" in the Add-on Store (you might need to refresh).
    * Click "Install" and wait for it to complete.
3.  **Configure Add-on:**
    * Go to the "Configuration" tab for the add-on.
    * Set your desired `ping_interval`, `speedtest_interval`, and `host`.
    * **Crucially, configure your MQTT settings** (`mqtt_host`, `mqtt_port`, etc.) to match your MQTT broker setup. The default `mqtt_host: core-mosquitto` assumes you are using the official Mosquitto broker addon.
4.  **Start Add-on:**
    * Go to the "Info" tab and click "Start".
    * Check the "Log" tab to ensure it starts without errors.

## Accessing the Web UI

Once the add-on is running, you should be able to access its web UI:
- If you have Ingress enabled for the addon, click "Open Web UI" on the addon's page, or find it in your Home Assistant sidebar under "SpeedTest Monitor".

## MQTT Sensors

If MQTT discovery is enabled and correctly configured, the following sensors should appear automatically in Home Assistant:

-   `binary_sensor.internet_connectivity`
-   `sensor.internet_ping`
-   `sensor.internet_download_speed`
-   `sensor.internet_upload_speed`

Make sure your MQTT integration in Home Assistant is set up to allow discovery or configure the sensors manually if needed.
The MQTT availability topic `homeassistant/sensor/speedtest_monitor/availability` can be used to track if the addon is publishing data.

## Troubleshooting

-   **"speedtest-cli not found"**: This addon assumes `speedtest-cli` is installed in its environment. This should be handled by your Dockerfile for the addon (not provided in this review, but necessary). You'll need to ensure `speedtest-cli` is installed.
-   **MQTT Connection Issues**: Double-check all MQTT settings in the addon configuration. Ensure your MQTT broker is accessible from the addon. Check the addon logs for detailed error messages.
-   **Web UI Not Updating / Showing Old Data**:
    * Ensure the `speedtest.py` script has write permissions to `/data/speedtest_results.json`.
    * Check addon logs for errors related to file writing or reading.
    * The web page auto-refreshes every 60 seconds.

## Development
This addon consists of:
- `speedtest.py`: The core Python script for tests and MQTT.
- `webserver.py`: A Flask web server for the Ingress UI.
- `run.sh`: Script to start the services.
- `config.yaml`: Addon configuration for Home Assistant.
- `templates/index.html`: The HTML page for the UI.