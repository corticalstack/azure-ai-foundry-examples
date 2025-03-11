# Azure OpenAI SDK Chat Client Example

## Introduction

This is a simple example application demonstrating how to use the Azure OpenAI SDK to create a chat client that connects directly to an Azure OpenAI endpoint deployed , sends message history to a language model, and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure OpenAI SDK**: Models are consumed through a direct connection to an Azure OpenAI endpoint using an API key, rather than through the Azure AI Foundry project client.

This example showcases:
- How to initialize the Azure OpenAI chat client directly
- How to authenticate using an API key
- How to send prompts and receive responses using the Azure OpenAI SDK
- How to maintain conversation context across multiple exchanges

## Setup Guide

### Prerequisites

- Azure account with access to Azure AI services
- An Azure OpenAI endpoint and API key
- VS Code with Dev Containers extension installed
- Docker installed on your system

### Using Dev Container

This project includes a development container configuration that sets up all necessary dependencies automatically.

To launch the dev container:

1. Open the project folder in VS Code
2. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev Containers: Reopen in Container"
3. VS Code will build the container and set up the environment (this may take a few minutes the first time)
4. Once the container is running, you'll have a fully configured environment with all dependencies installed

### Manual Setup (without Dev Container)

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

## Environment Configuration

The application uses environment variables for configuration, which are loaded from a `.env` file:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Azure OpenAI endpoint and API key:
   ```
   AZURE_INFERENCE_ENDPOINT=your-endpoint-url
   AZURE_INFERENCE_API_KEY=your-api-key
   ```

   Note: The endpoint URL should include the deployment name, e.g., `https://<resource-name>.openai.azure.com/openai/deployments/<deployment-name>/`

3. Optionally, adjust the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL):
   ```
   LOG_LEVEL=INFO
   ```

## Running the Application

1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python 04-azure-openai-sdk-chat-client/app.py
   ```
3. Enter your questions when prompted
4. The application maintains conversation history for context, so follow-up questions work naturally
5. Type 'clear' to reset the conversation history
6. Type 'quit' to quit the application

## Logging

The application uses Python's built-in logging module to log information at different levels:

- **DEBUG**: Detailed information, typically useful for debugging
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the application still works
- **ERROR**: Due to a more serious problem, the application has not been able to perform a function
- **CRITICAL**: A serious error, indicating that the application itself may be unable to continue running

Logs are written to a `04-azure-openai-sdk-chat-client.log` file in the application directory to avoid polluting the chat output.

## Key Differences from Other Examples

This example differs from the other examples in the following ways:

1. **Direct Connection**: Instead of connecting through an Azure AI Foundry project, this example connects directly to an Azure OpenAI endpoint using an API key.

2. **Client Creation**: This example uses `AzureOpenAI` from the `openai` package with direct endpoint and API key:
   ```python
   chat_client = AzureOpenAI(
       api_key=api_key,
       api_version="2024-10-21",
       azure_endpoint=base_endpoint
   )
   ```

3. **API Usage**: This example uses the OpenAI client's chat completions API:
   ```python
   response = chat_client.chat.completions.create(
       model=deployment_name,  # The deployment name is used as the model
       messages=conversation_history,
       max_tokens=4096,
       temperature=0.7,
       top_p=1,
       stop=None
   )
   ```

4. **Deployment Handling**: This example extracts the deployment name from the endpoint URL and stores it as an attribute of the client. It also correctly derives the base endpoint URL (e.g., `https://<resource-name>.openai.azure.com/`) from the full endpoint URL that includes the deployment name. The application requires a properly formatted endpoint URL that includes the deployment name (e.g., `/deployments/<deployment-name>/`) and will raise an exception if it's not found.
