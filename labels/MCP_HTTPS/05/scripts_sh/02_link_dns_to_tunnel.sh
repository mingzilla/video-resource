#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source ./scripts_sh/_common_utils.sh
# ======================

cloudflared::source_env ".env"

TUNNEL_NAME="$TUNNEL_NAME"
MAIN_DOMAIN="$MAIN_DOMAIN"
CLOUDFLARED_TOKEN="$CLOUDFLARED_TOKEN"

cloudflared::validate::installation
cloudflared::validate::tunnel_existence "$TUNNEL_NAME"

echo "Creating DNS records..."
echo "=================================================="

cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-traefik"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-schema-info-api"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-schema-info-mcp"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-company-search-api"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-company-search-mcp"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-rtic-checker-api"
cloudflared::dns::cname::create_or_update "$CLOUDFLARED_TOKEN" "$MAIN_DOMAIN" "$TUNNEL_NAME" "home-rtic-checker-mcp"

echo "DNS records created successfully!"
echo "Note: CNAME config takes about 15 minutes to propagate. To ensure valid config, visit"
echo "https://www.whatsmydns.net/"
echo "Search e.g. home-rtic-checker-mcp.$MAIN_DOMAIN"
