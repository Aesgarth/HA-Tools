# Use the Home Assistant base image
FROM homeassistant/amd64-base:3.18

# Set the working directory
WORKDIR /app

# Install Python and required libraries
RUN apk add --no-cache python3 py3-pip && pip3 install flask requests

# Copy the app folder into the container
COPY app /app

# Set up S6 service for the Flask app
RUN mkdir -p /etc/services.d/grocy-itemscanner
COPY run.sh /etc/services.d/grocy-itemscanner/run
RUN chmod +x /etc/services.d/grocy-itemscanner/run

# Expose the Flask port
EXPOSE 5080
