## Project docker-compose.yml File structure

The system has multiple projects, each project has docker compose files divided into DEV and PROD

- DEV - developed locally
- PROD - my-machine - deploy on my machine to run apps - .env 1
- PROD - office-machine - devops team deploy on office machine to run apps - .env 2

```text
ROOT
|-- <projectX> - https://www.<projectX>-api.my-domain.co.uk, https://www.<projectX>-mcp.my-domain.co.uk
|   |-- docker-compose.dev.yml  # DEV  - Uses 3xxxx ports - For local development & testing (OUT OF SCOPE - in this conversation)
|   +-- docker-compose.yml      # PROD - Uses 4xxxx ports - For production deployment (This is what we need to deal with)
|
+-- docker-compose.yml # PROD - PROD (my-machine): my-domain.co.uk; PROD (office-machine): <to-be-decided-later>.com
```

## Access Flow/Pattern:

```text
PROD (my-machine) - one project - api / mcp:
|-- https://www.<project1>-api.my-domain.co.uk
    |-> Cloudflare secure tunnel
        |-> My machine - project1/docker-compose.yml: `docker compose up -d` (has both API,MCP)
            |-> Traefik -> projectX API

PROD (my-machine) - all projects - api / mcp:
|-- https://www.<projectX>-api.my-domain.co.uk
    |-> Cloudflare secure tunnel
        |-> My machine - ROOT docker-compose.yml: `docker compose up -d` (has both API,MCP)
            |-> Traefik -> projectX API

PROD (office-machine) - all projects - api / mcp:
|-- https://www.<projectX>-api.<to-be-decided-later>.com
    |-> Cloudflare secure tunnel
        |-> Office machine - ROOT docker-compose.yml - `docker compose up -d` (has both API,MCP)
            |-> Traefik -> projectX API

Note: No certificate config. HTTPS auto-managed by Cloudflare
```

## Expectation

- API/MCP - Anyone can access PROD from the internet
- PROD - my-machine and office-machine deployment should be identical, except minimum envvars changes
- Release: Give ROOT/docker-compose.yml + .env.example to devops team -> change .env -> `docker compose up -d`
