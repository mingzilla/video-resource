#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source ./scripts_sh/_common_utils.sh
# ======================

cloudflared::source_env ".env"

TUNNEL_NAME="$TUNNEL_NAME"

echo "🚀 Starting Cloudflare Tunnel Setup..."
echo "-----------------------------------------"
cloudflared::validate_installation # 1
cloudflared::find_or_create_cert # 2. Authenticate with Cloudflare (if needed)
cloudflared::find_or_create_tunnel "$TUNNEL_NAME"
cloudflared::set_tunnel_token_to_dotenv "$TUNNEL_NAME" ".env" # docker-compose.yml needs this
cloudflared::activate_tunnel_with_config "$TUNNEL_NAME"
cloudflared::show_tunnel_url_and_cname_config_instructions "$TUNNEL_NAME"