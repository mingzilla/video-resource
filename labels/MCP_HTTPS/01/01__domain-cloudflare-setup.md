# Buy a domain and give it to Cloudflare

## Godaddy - Domain
- https://dcc.godaddy.com/control/portfolio/mingzillastudio.co.uk/settings?ventureId=3276f88d-00da-4040-a0bf-3b07ced63808&ua_placement=shared_header&subtab=nameservers
- Domain -> Nameservers -> Change Nameservers ->
  - alice.ns.cloudflare.com
  - colin.ns.cloudflare.com

## Cloudflare

### Connect a Domain
- https://dash.cloudflare.com/9eeb20c19e6f5160a1231beb6d80fa4d/mingzillastudio.co.uk
- Add -> Connect a Domain
- Follow the Wizard

### Verify Results

- https://www.whatsmydns.net/#A/mingzillastudio.co.uk

```shell
whois mingzillastudio.co.uk
```

### Verify Results 2
- https://dash.cloudflare.com/9eeb20c19e6f5160a1231beb6d80fa4d/mingzillastudio.co.uk/dns/records