### HTTPS MCP Request Flow

```
[Browser]
    | HTTPS Request (my-mcp.my-domain.co.uk)
    |--(HTTPS)
    ↓
[Cloudflare DNS]
    ↓ CNAME records (provides definitions): Maps subdomains to tunnel UUID
[Cloudflare Edge Servers]
    | Edge Servers (executes definitions): Forwards requests to tunnel
    | (Includes header: `Host: my-mcp.my-domain.co.uk`, for Traefik to know what sends a request to it)
    |--(QUIC/HTTP2 Tunnel)
    ↓
[Docker: Cloudflared - Cloudflare Tunnel]
    ↓--(HTTP) Receives Cloudflare requests -> Send HTTP request to http://traefik:80
[Docker: Traefik - Reverse Proxy]
    ↓--(HTTP) Serves http://traefik:80 -> Routes sub-domain-x requests -> http://container-name:4xxxx
[Docker: App]
    |--(HTTP) Serves http://container-name:4xxxx -> Handles request (Note: 4xxxx is docker internal port)
    | Returns response - flows back through same path
    |--(QUIC/HTTP2 Tunnel)
    ↓
[Cloudflare]
    |--(HTTPS)
    ↓
[Browser]
```