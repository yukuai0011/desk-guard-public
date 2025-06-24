# Use the official uv image as base
FROM ghcr.io/astral-sh/uv:debian-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and camera access
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./

# Sync dependencies using uv
RUN uv sync

# Copy the rest of the project files
COPY app.py ./

# Expose the port that Gradio uses
EXPOSE 7860

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application using uv
CMD ["uv", "run", "app.py"] 