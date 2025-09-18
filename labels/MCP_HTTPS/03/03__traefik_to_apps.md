## Tunnel → Local Traefik

**Why this connection exists:**

- Routes incoming requests to appropriate internal services
- Provides load balancing and service discovery
- Centralizes routing configuration for all applications

**How it works technically:**

- Cloudflare tunnel forwards HTTP requests to `traefik:80`
- Traefik examines the `Host` header to determine routing
- Docker network enables container-to-container communication

**Configuration required:**

1. **Traefik container setup** - Use docker-compose.gateway.yml

2. **Docker network connectivity - just use `default`**

3. **Environment variables** - MAIN_DOMAIN, CLOUDFLARE_TUNNEL_TOKEN

**Troubleshooting this connection:**

```bash
# Test tunnel to Traefik connectivity
docker exec cloudflared wget -qO- http://traefik:80
# Should get response from Traefik (may be 404 if no routes)

# Test Traefik receives requests
docker logs traefik --tail 20
# Should show request logs when you make HTTPS requests
```
