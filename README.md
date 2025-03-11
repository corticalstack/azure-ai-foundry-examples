# Azure AI Foundry Examples

This repository contains examples demonstrating how to use Azure AI Foundry services.

## Examples

- [01-project-based-model-inference-chat-client](./01-project-based-model-inference-chat-client/README.md): A simple example application demonstrating how to use the Azure AI Foundry Python SDK to create a chat completion client via a foundry project for Azure AI model inference.
- [02-project-based-openai-chat-client](./02-project-based-openai-chat-client/README.md): An example application demonstrating how to use the Azure AI Foundry Python SDK to create an Azure OpenAI client cia a foundry project for interacting with Azure OpenAI service.
- [03-direct-inference-sdk-chat-client](./03-direct-inference-sdk-chat-client/README.md): An example application demonstrating how to use the Azure AI Inference SDK to directly connect to an Azure AI Inference endpoint using an API key.
- [04-azure-openai-sdk-chat-client](./04-azure-openai-sdk-chat-client/README.md): An example application demonstrating how to use the Azure OpenAI SDK to directly connect to a foundry-deployed Azure OpenAI endpoint using an API key.

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
