#!/bin/bash

# Build the custom Ollama image with pre-installed model
echo "Building custom Ollama image with nomic-embed-text model..."
docker build -t mingzilla/ollama-nomic-embed:1.0.3 -f Dockerfile.ollama .

echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "docker login"
echo "docker push mingzilla/ollama-nomic-embed:1.0.3"