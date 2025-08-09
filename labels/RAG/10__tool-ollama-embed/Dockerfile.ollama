FROM ollama/ollama:0.9.6

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a directory for the model
RUN mkdir -p /root/.ollama

# Start Ollama server, pull the model, and then stop the server
RUN ollama serve & \
    timeout 120 bash -c 'while ! curl -s http://localhost:11434 >/dev/null; do sleep 1; done' && \
    ollama pull nomic-embed-text && \
    pkill ollama

# Set the entrypoint to start Ollama
ENTRYPOINT ["ollama"]
CMD ["serve"]

# Expose the Ollama API port
EXPOSE 11434

# Set working directory
WORKDIR /root