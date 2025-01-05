FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    nginx \
 && rm -rf /var/lib/apt/lists/*

# Create a directory for the addon
WORKDIR /app

# Copy the static "Hello World" web page
COPY www /app/www

# Copy the nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the ingress port
EXPOSE 3456

# Start nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
