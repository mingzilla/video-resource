#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source ./scripts_sh/_common_utils.sh
# ======================

cloudflared::source_env ".env"

TUNNEL_NAME="$TUNNEL_NAME"

echo "🚀 Starting Cloudflare Tunnel Setup..."
echo "========================================="
echo ""
echo "1. --------------------------------------"
cloudflared::validate::installation # 1
echo ""
echo "2. --------------------------------------"
cloudflared::cert::find_or_create # 2. Authenticate with Cloudflare (if needed)
echo ""
echo "3. --------------------------------------"
cloudflared::tunnel::find_or_create "$TUNNEL_NAME"
echo ""
echo "4. --------------------------------------"
cloudflared::tunnel::set_token_to_dotenv "$TUNNEL_NAME" ".env" # docker-compose.yml needs this
echo ""
echo "5. --------------------------------------"
cloudflared::tunnel::activate_with_config "$TUNNEL_NAME"
echo ""
echo "6. --------------------------------------"
cloudflared::tunnel::show_url_and_cname_config_instructions "$TUNNEL_NAME"