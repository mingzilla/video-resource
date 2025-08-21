## **Host networking in docker-compose:**

```yaml
services:
  ollama:
    image: mingzilla/ollama-nomic-embed:1.0.3
    container_name: ollama-service
    network_mode: "host"  # ← This is the key change
    # Remove the ports section - not needed and CANNOT REMAP with host networking
    environment:
      - OLLAMA_HOST=0.0.0.0  # Still recommended
    restart: unless-stopped
```

## **Comparison:**

| Bridge Mode (current)                | Host Mode                     |
|--------------------------------------|-------------------------------|
| 2 separate networks                  | 1 shared network              |
| Port mapping required: `11435:11434` | No port mapping               |
| Access: `localhost:11435`            | Access: `localhost:11434`     |
| Container isolated                   | Container shares host network |

## **What happens with host networking:**

```text
Your Machine Network (192.168.1.100)
|-- Ollama container runs directly on this network
|-- No separate Docker bridge network
|-- No port mapping needed
+-- Access directly: localhost:11434 (container's actual port)
```

## **Trade-offs:**

| Pro                         | Con                              |
|-----------------------------|----------------------------------|
| ✅ Simpler networking        | ❌ Less container isolation       |
| ✅ Better performance        | ❌ Port conflicts possible        |
| ✅ No port mapping confusion | ❌ Container can see host network |

**For local development, host networking is often the simpler choice!**