# 🤖 Azure AI Foundry Examples

This repository contains examples demonstrating how to work with Azure AI Foundry and it's assets.

## 🔧 Prerequisites

To run the examples in this repository, you'll need to have the following resources deployed in your Azure AI Foundry environment:

- A text generation model like gpt-4o-mini
- An embedding model like text-embedding-3-small
- An AI search service (ideally with the semantic reanker option enabled)

Make sure these resources are properly deployed and configured before running the examples.

## 📚 Examples

1️⃣ [01-explore-hub-and-projects](./01-explore-hub-and-projects/explore-hub-and-projects.ipynb): A notebook to explore your Azure AI Foundry hub, associated projects, connections, and service deployments.

2️⃣ [02-project-based-model-inference-chat-client](./02-project-based-model-inference-chat-client/README.md): A simple example showing how to use the Azure AI Foundry Python SDK to create a chat completion client via a foundry project for Azure AI model inference.

3️⃣ [03-project-based-openai-chat-client](./03-project-based-openai-chat-client/README.md): Another simple example demonstrating using the Azure AI Foundry Python SDK to create an Azure OpenAI client via a foundry project for interacting with Azure OpenAI service.

4️⃣ [04-azure-openai-sdk-chat-client](./04-azure-openai-sdk-chat-client/README.md): An example demonstrating how to use the Azure OpenAI SDK to directly connect to a foundry-deployed Azure OpenAI endpoint using an API key.

5️⃣ [05-direct-inference-sdk-chat-client](./05-direct-inference-sdk-chat-client/README.md): An example showing how to use the Azure AI Inference SDK to directly connect to an Azure AI Inference endpoint using an API key.

6️⃣ [06-direct-inference-sdk-streaming-chat-client](./06-direct-inference-sdk-streaming-chat-client/README.md): An example chat app using the Azure AI Inference SDK with asynchronous streaming responses.

7️⃣ [07-direct-inference-with-prompt-template](./07-direct-inference-with-prompt-template/README.md): An example application showing how to use the Azure AI Inference SDK with prompt templates.

8️⃣ [08-direct-inference-with-prompty-file](./08-direct-inference-with-prompty-file/README.md): An example using the Azure AI Inference SDK for text generation with .prompty files to load a prompt template containing a model configuration and system prompt.

9️⃣ [09-project-based-ai-search](./09-project-based-ai-search/README.md): A notebook demonstrating how to the default Azure AI Search connected to an Azure AI Foundry project to create a search index, upload documents, and perform a variety of search operations including exact match, fuzzy, vector, similarity, and hybrid.

## 🛠️ Setup Guide

### Requirements Management

- The root `requirements.txt` file includes all dependencies needed for all examples in the repository.

### 🐳 Using the Dev Container

This repository includes a development container configuration that sets up all necessary dependencies automatically. The dev container is configured to work with all examples in this repository.

1. ✅ Open the project folder in VS Code
2. ✅ When prompted, click "Reopen in Container" or use the command palette and select *Dev Containers: Reopen in Container*
3. ✅ VS Code will build the container and set up the environment (this may take a few minutes the first time)
4. ✅ Once the container is running, you'll have a fully configured environment with all dependencies installed
5. ✅ The dev container includes the Azure CLI for authentication. Use `az login` to authenticate with your Azure account

### 🔧 Manual Setup (without Dev Container)

If you prefer not to use the dev container:

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you're authenticated with Azure:
   ```bash
   az login
   ```

### ⚙️ Environment Configuration

Most examples in this repository use environment variables for configuration, which are loaded from a `.env` file:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add the required configuration values specific to each example.
   - Project-based examples typically require an Azure AI Foundry project connection string
   - Direct SDK examples typically require an endpoint URL and API key

3. Optionally, adjust the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL):
   ```
   LOG_LEVEL=INFO
   ```

### 📝 Logging

The examples use Python's built-in logging module to log information at different levels:

- **DEBUG**: Detailed information, typically useful for debugging
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the application still works
- **ERROR**: Due to a more serious problem, the application has not been able to perform a function
- **CRITICAL**: A serious error, indicating that the application itself may be unable to continue running

Logs are written to example-specific log files in the application directory to avoid polluting the example output.

## 👨‍💻 Contributing

Contributions and suggestions are welcome! Please see the [contributing guidelines](CONTRIBUTING.md) for details.

## 📖 Supplementary Documentation

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry)
- [Azure AI Inference API Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/reference-model-inference-api?view=azureml-api-2&tabs=python)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## ❓ FAQ

<details>
<summary><strong>What is Azure AI Foundry?</strong></summary>
A successor to Azure AI Studio, it's a home for AI capabilities including a collection of tools and services to fully create, manage, and use AI models at scale for data scientists and AI engineers.
</details>

<details>
<summary><strong>What is the difference between an Azure AI Foundry hub and project?</strong></summary>
A Hub is a parent workspace that provides shared resources including storage, key vault, and compute for multiple child Projects. Projects are lighter weight workspaces for managing AI components that inherit and use the Hub's resources. Think of Hubs as infrastructure and resource providers and Projects as workspaces for specific AI development efforts.
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
