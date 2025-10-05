#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source ./scripts_sh/_common_utils.sh
# ======================

cloudflared::source_env ".env"

TUNNEL_NAME="$TUNNEL_NAME"
MAIN_DOMAIN="$MAIN_DOMAIN"
CLOUDFLARED_TOKEN="$CLOUDFLARED_TOKEN"

cloudflared::validate_installation
cloudflared::validate_tunnel_existence "$TUNNEL_NAME"

echo "Creating DNS records..."
echo "=================================================="

cloudflared::create_or_update_cname "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-traefik"
cloudflared::create_or_update_cname "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-my-service-api"
cloudflared::create_or_update_cname "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-my-service-mcp"

echo "DNS records created successfully!"
echo "Note: CNAME config takes about 15 minutes to propagate. To ensure valid config, visit"
echo "https://www.whatsmydns.net/"
echo "Search e.g. home-my-service-mcp.$MAIN_DOMAIN"
