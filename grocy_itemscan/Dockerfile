FROM homeassistant/amd64-base:3.18

# Set working directory
WORKDIR /app

# Copy the add-on files
COPY run.sh /etc/services.d/grocy-scanner/run
RUN chmod +x /etc/services.d/grocy-scanner/run

# Expose ports
EXPOSE 5000
