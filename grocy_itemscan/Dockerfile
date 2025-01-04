# Use the Home Assistant base image
FROM homeassistant/amd64-base:3.18

# Set the working directory
WORKDIR /app

# Install Python and required libraries
RUN apk add --no-cache python3 py3-pip && pip3 install flask requests

# Copy application script
COPY app /app/app

# Copy templates and static files
COPY templates /app/templates
COPY static /app/static

# Set up S6 service for the Flask app
RUN mkdir -p /etc/services.d/grocy-itemscanner
COPY run.sh /etc/services.d/grocy-itemscanner/run
RUN chmod +x /etc/services.d/grocy-itemscanner/run

# Expose the port for the Flask app
EXPOSE 5080
