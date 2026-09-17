FROM python:3.11-slim

# Install FFmpeg (essential for video rendering/conversion)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Expose port (Render sets PORT env var)
EXPOSE 3000

# Start the server
CMD ["python", "server.py"]

