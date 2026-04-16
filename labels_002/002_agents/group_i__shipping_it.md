# I. Shipping It

- [27. Docker — tokens without a browser]
- [28. Docker — Claude CLI refuses root]

---

## The Problem

The system works on Ming's laptop. Now it needs to run on a server — headless,
no GUI, no browser, possibly no human nearby. Claude Code requires authentication.
Docker is the deployment target.

```text
Ming's laptop:                     Server (Docker):
  +-------------------+              +-------------------+
  | claude login      |              | claude login      |
  | (browser opens)   |              | (no browser)      |
  | (click approve)   |              | (???)             |
  | (done)            |              |                   |
  +-------------------+              +-------------------+

  Also:
  +-------------------+              +-------------------+
  | runs as: ming     |              | runs as: root     |
  | (non-root)        |              | (default Docker)  |
  | (works fine)      |              | (Claude refuses)  |
  +-------------------+              +-------------------+
```

---

## Decision 27: Tokens without a browser

> You thought: claude login inside Docker.
> But actually: claude setup-token — generates a 1-year token, no browser needed.

```text
OPTION A: claude login (rejected)

  docker exec -it rtic_qa bash
  $ claude login
  --> "Opening browser at https://..."
  --> No browser in Docker.
  --> Fails.


OPTION B: copy ~/.claude/ from host (rejected)

  # On host: log in as RTIC account
  claude logout
  claude login  --> browser, authenticate as RTIC account
  cp -r ~/.claude/* /path/to/docker/volume/

  # Switch back
  claude logout
  claude login  --> browser, authenticate as work account

  Problems:
  - Fragile — auth files are internal, format may change
  - Disruptive — have to log out of work account temporarily
  - Manual — repeat every time token expires


OPTION C: claude setup-token (chosen)

  # On ANY machine, ANY OS:
  $ claude setup-token

  Your OAuth token (valid for 1 year):
  sk-xxxxxxxxxxxxxxxxxxxxxxxxxx

  Store this token securely. You won't be able to see it again.
  Use this token by setting: export CLAUDE_CODE_OAUTH_TOKEN=<token>

  # Put in config file:
  claude_auth.json:
  {
    "claude_oauth_tokens": ["sk-xxxxxxxxxx"],
    "claude_oauth_tokens_expiry_date": "2027-04-03"
  }

  # Docker reads config via volume mount.
  # No browser. No login. No ~/.claude/ to manage.
  # Token lasts 1 year. Renew with one command.

  # Multiple subscriptions? Multiple tokens:
  {
    "claude_oauth_tokens": [
      "sk-token-rtic-account",
      "sk-token-george-account"
    ]
  }
```

- **Q:** how to authenticate Claude Code in Docker with no browser?
- **Options:** (a) `claude login` (needs browser), (b) copy `~/.claude/`, (c) `claude setup-token`
- **Chose:** setup-token generates a 1-year OAuth token set via env var
- **Why:** no browser needed. A string in a config file. Works anywhere.

---

## Decision 28: Claude CLI refuses root

> You thought: run as root in the container.
> But actually: Claude CLI refuses --dangerously-skip-permissions as root. Non-root user required.

```text
AS ROOT (fails):

  Dockerfile:
    FROM python:3.13-slim
    WORKDIR /app
    COPY . .
    CMD ["claude", "-p", "..."]

  $ docker run rtic-qa
  Error: --dangerously-skip-permissions cannot be used as root

  Claude CLI enforces this. No workaround. No flag to override.


AS NON-ROOT (chosen):

  Dockerfile:
    FROM python:3.13-slim

    # Create non-root user
    RUN useradd -m -s /bin/bash appuser

    # Install uv as root (system-wide)
    RUN curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install Claude CLI as appuser
    USER appuser
    RUN curl -fsSL https://claude.ai/install.sh | bash

    # Set up app
    USER root
    WORKDIR /app
    COPY . .
    RUN uv sync --no-dev

    # Run as appuser
    USER appuser
    CMD ["uv", "run", "python", "src/m001_qa_server/main.py"]

  Key details:
    - Claude CLI installed AS appuser (not root)
    - App runs AS appuser
    - Volume dirs need appuser ownership:
      RUN mkdir -p /app/config /app/runs && chown -R appuser:appuser /app
```

- **Q:** how to containerise the system?
- **Options:** none — hard constraint
- **Chose:** non-root user in Dockerfile, install and run Claude as that user
- **Why:** Claude CLI enforces this. No workaround.
- **Constraint:** Dockerfile must create non-root user, install Claude CLI as that user, chown volume directories
