#!/bin/bash

# This script automates the setup of a Cloudflare Tunnel and retrieves its token.
# It is designed to be idempotent and safe to run multiple times.

set -e

# --- Configuration ---
TUNNEL_NAME="ai-integration-tunnel"

echo "🚀 Starting Cloudflare Tunnel Setup..."
echo "-----------------------------------------"

# --- 1. Dependency Check ---
echo "🔎 Checking for 'cloudflared' command..."
if ! command -v cloudflared &> /dev/null; then
    echo "❌ Error: 'cloudflared' is not installed. Please install it and re-run."
    # Add installation instructions or automation here if desired in the future.
    exit 1
fi
echo "✅ 'cloudflared' is installed."

# --- 2. Authenticate with Cloudflare (if needed) ---
# The login command creates cert.pem in the default directory.
if [ -f "$HOME/.cloudflared/cert.pem" ]; then
    echo "
🔐 Already logged in to Cloudflare."
else
    echo "
🔐 Authenticating with Cloudflare..."
    echo "A browser window will open for you to log in."
    read -p "Press [Enter] to continue..."
    cloudflared login
    echo "✅ Authentication successful."
fi

# --- 3. Create Tunnel (if needed) ---
echo "
🚇 Checking for Cloudflare Tunnel named '$TUNNEL_NAME'..."

# Check if tunnel exists by grepping the list output.
if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "✅ Tunnel '$TUNNEL_NAME' already exists."
else
    echo " -> Tunnel not found. Creating it now..."
    cloudflared tunnel create "$TUNNEL_NAME"
    echo "✅ Tunnel created successfully."
fi

# --- 4. Get and Display Token ---
echo "
🔑 Retrieving the token for '$TUNNEL_NAME'..."

# This command communicates with the Cloudflare API using your login credentials.
# It does not depend on the local tunnel credential JSON file.
TOKEN=$(cloudflared tunnel token "$TUNNEL_NAME")

if [ -z "$TOKEN" ]; then
    echo "❌ Error: Could not retrieve the tunnel token."
    exit 1
fi

echo "
🎉 All done! Here is your tunnel token:"
echo ""
echo "======================================================================"
echo "$TOKEN"
echo "======================================================================"
echo ""
echo "Next step: Copy this token into your .env file as CLOUDFLARE_TUNNEL_TOKEN"
