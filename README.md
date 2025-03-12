# Azure AI Foundry Examples

This repository contains examples demonstrating how to use Azure AI Foundry services.

## Examples

- [01-project-based-model-inference-chat-client](./01-project-based-model-inference-chat-client/README.md): A simple example application demonstrating how to use the Azure AI Foundry Python SDK to create a chat completion client via a foundry project for Azure AI model inference.
- [02-project-based-openai-chat-client](./02-project-based-openai-chat-client/README.md): An example application demonstrating how to use the Azure AI Foundry Python SDK to create an Azure OpenAI client via a foundry project for interacting with Azure OpenAI service.
- [03-direct-inference-sdk-chat-client](./03-direct-inference-sdk-chat-client/README.md): An example application demonstrating how to use the Azure AI Inference SDK to directly connect to an Azure AI Inference endpoint using an API key.
- [04-azure-openai-sdk-chat-client](./04-azure-openai-sdk-chat-client/README.md): An example application demonstrating how to use the Azure OpenAI SDK to directly connect to a foundry-deployed Azure OpenAI endpoint using an API key.

## Development Container

This repository includes a development container configuration that sets up all necessary dependencies automatically. The dev container is configured to work with all examples in this repository.

### Requirements Management

- The root `requirements.txt` file includes all dependencies needed for all examples in the repository.

### Using the Dev Container

1. Open the project folder in VS Code
2. When prompted, click "Reopen in Container" or use the command palette (F1) and select *Dev Containers: Reopen in Container*
3. VS Code will build the container and set up the environment (this may take a few minutes the first time)
4. Once the container is running, you'll have a fully configured environment with all dependencies installed
5. The dev container includes the Azure CLI for authentication. Use `az login` to authenticate with your Azure account


## Contributing

Contributions and suggestions are welcome! Please see the [contributing guidelines](CONTRIBUTING.md) for details.

## Supplementary Documentation

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry)
- [Azure AI Inference API Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/reference-model-inference-api?view=azureml-api-2&tabs=python)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## FAQ

<details>
<summary><strong>What is Azure AI Foundry?</strong></summary>
A successor to Azure AI Studio, it's a home for AI capabilities including a collection of tools and services to fully create, manage, and use AI models at scale for data scientists and AI engineers.
</details>

<details>
<summary><strong>What is the difference between the managed compute and serverless API deployment options?</strong></summary>

Deployment options differ primarily in pricing structure and infrastructure approach.

**Serverless deployment**:
- Pay-as-you-go model based on token usage (input, output, and reasoning tokens)
- Runs on shared GPU cluster pools specific to each model
- Can utilize global pools, or region-specific pools (like East US or Sweden Central)

**Managed compute**:
- Hourly billing model regardless of usage
- Runs on dedicated virtual machines with the model and API pre-deployed
- Microsoft handles all infrastructure management and deployment
</details>

<details>
<summary><strong>What is the difference between the Azure AI inferencing API and OpenAI API?</strong></summary>

The Azure AI inferencing API (package `azure.ai.inference`) serves as an abstraction layer that allows applications to interact with various models using a standardized interface. It translates requests to the specific format required by each underlying model.

While `azure.ai.inference` provides a model-agnostic abstraction layer, the openai package with the AzureOpenAI client (i.e., `from openai import AzureOpenAI`) is specifically designed for interacting with OpenAI models deployed on Azure. 

In summary, the key benefit of `azure.ai.inference` is the ability to switch between supported models, for example between an OpenAI and Meta model, without modifying your application code, avoiding code lock-in.

Verify model compatibility via the [inference API documentation](https://learn.microsoft.com/en-us/azure/machine-learning/reference-model-inference-api?view=azureml-api-2&tabs=python).
</details>


