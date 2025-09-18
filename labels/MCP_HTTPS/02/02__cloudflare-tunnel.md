### 🔐 How to Get a `CLOUDFLARE_TUNNEL_TOKEN`

#### 1. **Install `cloudflared`**

If you haven’t already:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

---

#### 2. **Authenticate with Cloudflare**

```bash
cloudflared login
```

This opens a browser window. Log in and select your domain (e.g. `your-domain.com`). It creates a cert file locally at:

```
~/.cloudflared/cert.pem
```

---

#### 3. **Create a Named Tunnel**

```bash
cloudflared tunnel create ai-integration-tunnel
```

This generates a tunnel ID and stores credentials in:

```
~/.cloudflared/ai-integration-tunnel.json
```

---

#### 4. **Get the Tunnel Token**

You can now retrieve the token via:

```bash
cloudflared tunnel token ai-integration-tunnel
```

Or copy it from the Cloudflare dashboard:
- https://one.dash.cloudflare.com/
- Go to **Zero Trust > Access > Tunnels**
- Find your tunnel (`ai-integration-tunnel`)
- Click **Configure** → **Token** tab

---

### 🧠 Why This Works Without Certs

- Cloudflare terminates TLS at the edge
- Your local service (e.g. FastAPI, Docker container) connects outbound to Cloudflare
- No need to expose ports or manage Let’s Encrypt certs
- You get automatic HTTPS, DDoS protection, and routing
