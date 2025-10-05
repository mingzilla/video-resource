#!/bin/bash
set -e
cd "$(dirname "$0")/.."
# ======================

cmd::source_env() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
      set -a
      source <(sed 's/\r$//' "$env_file")
      set +a
    else
      echo "Error: .env file not found at $env_file"
      exit 1
    fi
}

cmd::validate_required() {
    local thing="$1"
    local message="$2"
    if [ -z "$thing" ]; then
        echo "❌ Error: $message." >&2
        return 1
    fi
}

cloudflared::source_env() {
    cmd::source_env "$1"
    echo "MAIN_DOMAIN: $MAIN_DOMAIN"
    echo "TUNNEL_NAME: $TUNNEL_NAME"
    echo "EXPOSE_DASHBOARD_WITHOUT_PASSWORD: $EXPOSE_DASHBOARD_WITHOUT_PASSWORD"
}

cloudflared::validate_installation() {
    echo "🔎 Checking for 'cloudflared' command..."
    if ! command -v cloudflared &> /dev/null; then
        echo "❌ Error: 'cloudflared' is not installed. Please install it and re-run."
        # Add installation instructions or automation here if desired in the future.
        exit 1
    fi
    echo "✅ 'cloudflared' is installed."
}

cloudflared::validate_tunnel_existence() {
    local tunnel_name="$1"
    if ! cloudflared tunnel list | grep -q "$tunnel_name"; then
        echo "Error: Tunnel '$tunnel_name' not found. Please run 01_tunnel_setup.sh first."
        exit 1
    fi
}

cloudflared::find_or_create_cert() {
    if [ -f "$HOME/.cloudflared/cert.pem" ]; then
        echo "🔐 Already logged in to Cloudflare."
    else
        echo "🔐 Authenticating with Cloudflare..."
        echo "A browser window will open for you to log in."
        read -p "Press [Enter] to continue..."
        cloudflared login
        echo "✅ Authentication successful."
    fi
}

cloudflared::find_or_create_tunnel() {
    local tunnel_name="$1"
    echo "🚇 Checking for Cloudflare Tunnel named '$tunnel_name'..."

    # Check if tunnel exists by grepping the list output.
    if cloudflared tunnel list | grep -q "$tunnel_name"; then
        echo "✅ Tunnel '$tunnel_name' already exists."
    else
        echo " -> Tunnel not found. Creating it now..."
        cloudflared tunnel create "$tunnel_name"
        echo "✅ Tunnel created successfully."
    fi
}

cloudflared::get_tunnel_token() {
    local tunnel_name="$1"
    echo "🔑 Retrieving the token for '$tunnel_name'..." >&2 # `>&2` avoids mixing this output with the token to be returned at the end
    cmd::validate_required "$tunnel_name" "Please supply tunnel name"

    token=$(cloudflared tunnel token "$tunnel_name")
    cmd::validate_required "$token" "Could not retrieve the tunnel token."

    echo "$token"
}

cloudflared::set_tunnel_token_to_dotenv() {
    local tunnel_name="$1"
    local env_file="$2"
    cmd::validate_required "$tunnel_name" "Please supply tunnel name"
    cmd::validate_required "$env_file" "Please supply an env file path"
    if [ ! -f "$env_file" ]; then
        echo ".env file not found."
        return 1
    fi

    local token=$(cloudflared::get_tunnel_token "$tunnel_name")
    cmd::validate_required "$token" "Failed to get a new tunnel token."

    # If not in file, add to end of file. If it's in file, delete it, add to end of file. Create .tmp because sh cannot read/write same file at the same time
    if grep -q "^CLOUDFLARE_TUNNEL_TOKEN=" "$env_file"; then
        echo "ℹ️ CLOUDFLARE_TUNNEL_TOKEN found in $env_file. Updating it..."
        # Use grep to filter out the old line and append the new one
        grep -v "^CLOUDFLARE_TUNNEL_TOKEN=" "$env_file" > "$env_file.tmp"
        echo "CLOUDFLARE_TUNNEL_TOKEN=$token" >> "$env_file.tmp"
        mv "$env_file.tmp" "$env_file"
    else
        echo "ℹ️ CLOUDFLARE_TUNNEL_TOKEN not found in $env_file. Adding it..."
        # If it doesn't exist, just append it
        echo "CLOUDFLARE_TUNNEL_TOKEN=$token" >> "$env_file"
    fi

    echo "✅ Successfully set CLOUDFLARE_TUNNEL_TOKEN in $env_file."
}

cloudflared::activate_tunnel_with_config() {
    local tunnel_name="$1"

    export CLOUDFLARE_TUNNEL_TOKEN=$(cloudflared::get_tunnel_token "$tunnel_name") # env var for docker compose yml file
    echo "$CLOUDFLARE_TUNNEL_TOKEN"

    docker compose -f docker-compose.activate-tunnel.yml up -d

    echo ""
    echo "======================================================================"
    echo "🚀 Go to https://one.dash.cloudflare.com/"
    echo "1. Select Account -> Networks (left) -> Tunnels: $tunnel_name should be healthy"
    echo "2. Select $tunnel_name -> Drop down -> Configure -> Start Migration -> Next, Next, Next"
    echo "3. Tunnel Route Config is done. Stop this container"
    echo "======================================================================"
    echo ""
}

cloudflared::get_tunnel_url() {
    local tunnel_name="$1"

    tunnel_id=$(cloudflared tunnel list | grep "$tunnel_name" | awk '{print $1}')

    if [ -z "$tunnel_id" ]; then
        echo "❌ Error: Could not retrieve the tunnel ID for tunnel '$tunnel_name'."
        exit 1
    fi

    tunnel_url="$tunnel_id.cfargotunnel.com"
    echo "$tunnel_url"
}

cloudflared::show_tunnel_url_and_cname_config_instructions() {
    local tunnel_name="$1"
    echo "🌐 Retrieving the Tunnel URL for '$tunnel_name'..."

    local tunnel_url=$(cloudflared::get_tunnel_url "$tunnel_name")

    echo ""
    echo "======================================================================"
    echo "🚀 Go to https://dash.cloudflare.com/"
    echo "1. Select Account -> DNS (left) -> Records"
    echo "2. Select Related CNAME config -> Edit -> Target"
    echo "3. Paste Tunnel URL:"
    echo "$tunnel_url"
    echo "4. Finish each relevant item"
    echo "Note: CNAME config takes about 15 minutes to propagate. To ensure valid config, visit"
    echo "https://www.whatsmydns.net/"
    echo "Search e.g. home-my-service-mcp.my-domain.co.uk"
    echo "======================================================================"
    echo ""
}

# Usage: cloudflared::create_cname_and_tunnel_route "$TUNNEL_NAME" "$MAIN_DOMAIN" "example-subdomain"
# This should work. If it doesn't in the future, use cloudflared::create_cname
cloudflared::create_cname_and_tunnel_route() {
    local tunnel_name="$1"
    local main_domain="$2"
    local cname="$3"
    cloudflared tunnel route dns "$tunnel_name" "$cname.$main_domain"
    echo "Created: https://$cname.$main_domain"
}

cloudflared::get_zone_id() {
    local cloudflare_token="$1"
    local domain_name="$2"
    cmd::validate_required "$cloudflare_token" "Cloudflare API token must be provided"
    cmd::validate_required "$domain_name" "Domain name must be provided"

    # Use the API to get the zone ID, suppressing curl's progress meter with -s
    local response
    response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$domain_name" \
         -H "Authorization: Bearer $cloudflare_token" \
         -H "Content-Type: application/json")

    # Basic parsing without needing jq
    local zone_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -n 1 | cut -d'"' -f4)
    cmd::validate_required "$zone_id" "Zone ID cannot be identified"

    echo "$zone_id"
}

cloudflared::find_cname_record_id() {
    local cloudflare_token="$1"
    local main_domain="$2"
    local cname_subdomain="$3"
    cmd::validate_required "$cloudflare_token" "Cloudflare API token must be provided"

    local full_record_name="$cname_subdomain.$main_domain"
    local zone_id=$(cloudflared::get_zone_id "$cloudflare_token" "$main_domain")

    local record_response
    record_response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?type=CNAME&name=$full_record_name" \
        -H "Authorization: Bearer $cloudflare_token" \
        -H "Content-Type: application/json")

    local record_id=$(echo "$record_response" | grep -o '"id":"[^"]*"' | head -n 1 | cut -d'"' -f4)
    echo "$record_id"
}

# Usage: #cloudflared::create_cname_and_tunnel_route "$TUNNEL_NAME" "$MAIN_DOMAIN" "example-subdomain"
cloudflared::create_cname() {
    local cloudflare_token="$1"
    local main_domain="$2"
    local tunnel_name="$3"
    local cname_subdomain="$4"
    cmd::validate_required "$cloudflare_token" "Cloudflare API token must be provided"

    local full_record_name="$cname_subdomain.$main_domain"
    local zone_id=$(cloudflared::get_zone_id "$cloudflare_token" "$main_domain")
    local tunnel_url=$(cloudflared::get_tunnel_url "$tunnel_name")

    local json_payload
    json_payload=$(printf '{"type":"CNAME","name":"%s","content":"%s","proxied":true}' "$full_record_name" "$tunnel_url")

    curl -X POST "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records" \
         -H "Authorization: Bearer $cloudflare_token" \
         -H "Content-Type: application/json" \
         --data "$json_payload"

    echo "✅ Created CNAME record for: https://$full_record_name"
}

# Updates an existing CNAME record with a new tunnel URL.
# Fails if the record does not exist.
# Usage: cloudflared::update_cname <api_token> <main_domain> <tunnel_name> <cname_subdomain>
cloudflared::update_cname() {
    local cloudflare_token="$1"
    local main_domain="$2"
    local tunnel_name="$3"
    local cname_subdomain="$4"
    cmd::validate_required "$cloudflare_token" "Cloudflare API token must be provided"

    local full_record_name="$cname_subdomain.$main_domain"
    local zone_id=$(cloudflared::get_zone_id "$cloudflare_token" "$main_domain")
    local tunnel_url=$(cloudflared::get_tunnel_url "$tunnel_name")
    local record_id=$(cloudflared::find_cname_record_id "$cloudflare_token" "$main_domain" "$cname_subdomain")
    cmd::validate_required "$record_id" "CNAME record for '$full_record_name' not found. Cannot update."

    local update_payload=$(printf '{"type":"CNAME","name":"%s","content":"%s","proxied":true}' "$full_record_name" "$tunnel_url")

    local update_response
    update_response=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$record_id" \
         -H "Authorization: Bearer $cloudflare_token" \
         -H "Content-Type: application/json" \
         --data "$update_payload")

    if echo "$update_response" | grep -q '"success":true'; then
        echo "✅ Updated CNAME record for: https://$full_record_name"
    else
        echo "❌ Error: Failed to update CNAME record for '$full_record_name'." >&2
        echo "API Response: $update_response" >&2
        return 1
    fi
}

# Creates a CNAME record if it doesn't exist, or updates it if it does.
# Usage: cloudflared::create_or_update_cname <api_token> <main_domain> <tunnel_name> <cname_subdomain>
cloudflared::create_or_update_cname() {
    local cloudflare_token="$1"
    local main_domain="$2"
    local tunnel_name="$3"
    local cname_subdomain="$4"
    cmd::validate_required "$cloudflare_token" "Cloudflare API token must be provided"

    local full_record_name="$cname_subdomain.$main_domain"
    local record_id=$(cloudflared::find_cname_record_id "$cloudflare_token" "$main_domain" "$cname_subdomain")

    if [ -z "$record_id" ]; then
        echo "ℹ️ No existing CNAME record found for '$full_record_name'. Creating a new one..."
        cloudflared::create_cname "$cloudflare_token" "$main_domain" "$tunnel_name" "$cname_subdomain"
    else
        echo "ℹ️ Existing CNAME record found for '$full_record_name'. Updating it..."
        cloudflared::update_cname "$cloudflare_token" "$main_domain" "$tunnel_name" "$cname_subdomain"
    fi
}
