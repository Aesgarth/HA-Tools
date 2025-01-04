# Use the Home Assistant base image
FROM homeassistant/amd64-base:3.18

# Set the working directory
WORKDIR /app

# Copy the service script to the S6 service directory
RUN mkdir -p /etc/services.d/grocy-itemscan
COPY run.sh /etc/services.d/grocy-itemscan/run
RUN chmod +x /etc/services.d/grocy-itemscan/run

# Expose ports for the service
EXPOSE 5000
