# Use the Home Assistant base image
FROM homeassistant/amd64-base:3.18

# Set the working directory
WORKDIR /app

# Install dependencies
RUN apk add --no-cache python3 py3-pip && pip3 install flask requests

# Copy the Flask application
COPY app.py /app/app.py
COPY templates /app/templates

# Set up the S6 service for the Flask app
RUN mkdir -p /etc/services.d/flask-app
COPY run.sh /etc/services.d/flask-app/run
RUN chmod +x /etc/services.d/flask-app/run

# Expose the port for the Flask app
EXPOSE 5080
