FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libzbar0 && \
    pip install --no-cache-dir flask requests

# Add your code
WORKDIR /app
COPY api/ /app/api/
COPY web_ui/ /app/web_ui/
COPY run.sh /app/

# Expose the port and set permissions
EXPOSE 8099
RUN chmod +x /app/run.sh

# Start the app
CMD ["/app/run.sh"]
