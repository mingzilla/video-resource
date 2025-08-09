#!/bin/bash

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Error: Version tag is required"
    echo "Usage: ./publish.sh <version>"
    echo "Example: ./publish.sh 1.0.2"
    exit 1
fi

VERSION=$1
IMAGE_NAME="mingzilla/ollama-nomic-embed"

echo "Publishing $IMAGE_NAME:$VERSION to Docker Hub..."

# Tag the image with version and latest
docker tag $IMAGE_NAME:latest $IMAGE_NAME:$VERSION

# Push both tags to Docker Hub
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Successfully published:"
echo "- $IMAGE_NAME:$VERSION"
echo "- $IMAGE_NAME:latest"