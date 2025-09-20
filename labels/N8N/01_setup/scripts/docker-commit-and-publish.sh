#!/bin/bash

# Generate version based on date and hour in 24-hour format
VERSION=$(date +"%Y-%m-%d_%H")

echo "Creating and publishing n8n image with version: $VERSION"

# Commit the running container to a new image
docker commit n8n example/n8n_no-auth:$VERSION

# Tag it as latest as well
docker tag example/n8n_no-auth:$VERSION example/n8n_no-auth:latest

# Push both tags
docker push example/n8n_no-auth:$VERSION
docker push example/n8n_no-auth:latest

echo "Successfully published example/n8n_no-auth:$VERSION and example/n8n_no-auth:latest"