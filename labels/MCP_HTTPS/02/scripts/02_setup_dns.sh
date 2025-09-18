#!/bin/bash

# This script sets up DNS records for the tunnel
# Run this after creating the tunnel with 01_tunnel_setup.sh

set -e

TUNNEL_NAME="ai-integration-tunnel"
DOMAIN="your-domain.com"

echo "Setting up DNS records for Cloudflare Tunnel..."
echo "=================================================="

# Check if cloudflared is available
if ! command -v cloudflared &> /dev/null; then
    echo "Error: 'cloudflared' is not installed."
    exit 1
fi

# Check if tunnel exists
if ! cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "Error: Tunnel '$TUNNEL_NAME' not found. Please run 01_tunnel_setup.sh first."
    exit 1
fi

echo "Creating DNS records..."

# Create DNS records for each subdomain
cloudflared tunnel route dns "$TUNNEL_NAME" "app1-api.$DOMAIN"
cloudflared tunnel route dns "$TUNNEL_NAME" "app1-mcp.$DOMAIN"
cloudflared tunnel route dns "$TUNNEL_NAME" "app2-api.$DOMAIN"
cloudflared tunnel route dns "$TUNNEL_NAME" "app2-mcp.$DOMAIN"
cloudflared tunnel route dns "$TUNNEL_NAME" "traefik.$DOMAIN"

echo "DNS records created successfully!"
echo ""
echo "The following URLs should now be accessible:"
echo "- https://app1-api.$DOMAIN"
echo "- https://app1-mcp.$DOMAIN"
echo "- https://app2-api.$DOMAIN"
echo "- https://app2-mcp.$DOMAIN"
echo "- https://traefik.$DOMAIN"
echo ""
echo "Note: DNS propagation may take a few minutes."