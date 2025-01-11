FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
       iputils-ping \
   && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --no-cache-dir paho-mqtt flask

# Copy the scripts and web interface files
WORKDIR /app
COPY run.sh /app/run.sh
COPY speedtest.py /app/speedtest.py
COPY webserver.py /app/webserver.py
COPY templates /app/templates

# Ensure scripts are executable
RUN chmod +x /app/run.sh /app/speedtest.py /app/webserver.py

# Expose the web server port
EXPOSE 3457

# Start the addon
CMD ["/app/run.sh"]