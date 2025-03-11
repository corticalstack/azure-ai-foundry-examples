# Azure AI Foundry Examples

This repository contains examples demonstrating how to use Azure AI Foundry services.

## Examples

- [01-azure-ai-model-inference-chat-client](./01-azure-ai-model-inference-chat-client/README.md): A simple example application demonstrating how to use the Azure AI Foundry Python SDK to create a chat completion client for Azure AI model inference.

## Development Container

This repository includes a development container configuration that sets up all necessary dependencies automatically. The dev container is configured to work with all examples in this repository.

### Requirements Management

- The root `requirements.txt` file includes all dependencies needed for all examples in the repository.
- Individual examples may have their own `requirements.txt` files for documentation purposes, but the dev container uses the root `requirements.txt` file.

### Using the Dev Container

1. Open the project folder in VS Code
2. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev Containers: Reopen in Container"
3. VS Code will build the container and set up the environment (this may take a few minutes the first time)
4. Once the container is running, you'll have a fully configured environment with all dependencies installed
5. The dev container includes the Azure CLI for authentication. Use `az login` to authenticate with your Azure account

### Adding New Examples

When adding new examples with additional dependencies:

1. Add the new dependencies to the root `requirements.txt` file
2. Rebuild the dev container to include the new dependencies

This ensures that the dev container will work with all examples in the repository.
