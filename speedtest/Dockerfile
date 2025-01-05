FROM python:3.11-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    iputils-ping \
    speedtest-cli \
 && rm -rf /var/lib/apt/lists/*

# Copy the scripts
WORKDIR /app
COPY run.sh /app/run.sh
COPY speedtest.py /app/speedtest.py

# Ensure scripts are executable
RUN chmod +x /app/run.sh /app/speedtest.py

# Start the addon
CMD ["/app/run.sh"]
