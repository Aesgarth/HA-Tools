# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
# - iputils-ping: for the ping command
# - speedtest-cli: for performing speed tests (the official CLI or a compatible version)
# - jq: for parsing JSON in shell scripts (used in run.sh)
# - curl: often useful for health checks or downloading, good to have
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    speedtest-cli \
    jq \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY run.sh /app/run.sh
COPY speedtest.py /app/speedtest.py
COPY webserver.py /app/webserver.py
COPY templates/ /app/templates/

# Make the run script executable
RUN chmod +x /app/run.sh

# Expose the port the web server runs on (as defined in config.yaml ingress_port)
EXPOSE 3457

# Define the command to run your application
CMD ["/app/run.sh"]