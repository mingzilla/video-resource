# Buy a domain and give it to Cloudflare

## Godaddy - Domain
- https://dcc.godaddy.com/control/
- Domain -> Nameservers -> Change Nameservers ->
  - alice.ns.cloudflare.com
  - colin.ns.cloudflare.com

## Cloudflare

### Connect a Domain
- https://dash.cloudflare.com/
- Add -> Connect a Domain
- Follow the Wizard

### Verify Results

- https://www.whatsmydns.net

```shell
sudo apt-get update
sudo apt-get install whois

whois mingzillastudio.co.uk
```

- https://dash.cloudflare.com
- domain -> dns -> records