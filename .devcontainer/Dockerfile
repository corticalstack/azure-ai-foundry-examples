FROM python:3.11-slim

# Set working directory to match the workspace folder in devcontainer.json
WORKDIR /workspaces/azure-ai-foundry-examples

# Install Python dependencies from root requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Note: This requirements.txt includes dependencies for all examples in the repository

# Install Azure CLI
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    lsb-release \
    gnupg \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install -y azure-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application
RUN useradd -m appuser \
    && chown -R appuser:appuser /workspaces

USER appuser

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1
