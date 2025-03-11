# Azure AI Inference SDK Chat Client Example

## Introduction

This is a simple example application demonstrating how to use the Azure AI Inference SDK to create a chat client that connects directly to an Azure AI Inference endpoint, sends message history to a language model, and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure AI Inference SDK**: Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, rather than through the Azure AI Foundry project client.

This example showcases:
- How to initialize the Azure AI Inference chat client directly
- How to authenticate using an API key
- How to send prompts and receive responses using the Azure AI Inference SDK
- How to maintain conversation context across multiple exchanges

## Setup Guide

### Prerequisites

- Azure account with access to Azure AI services
- An Azure AI Inference endpoint and API key
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

2. Edit the `.env` file and add your Azure AI Inference endpoint and API key:
   ```
   AZURE_INFERENCE_ENDPOINT=your-endpoint-url
   AZURE_INFERENCE_API_KEY=your-api-key
   ```

3. Optionally, adjust the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL):
   ```
   LOG_LEVEL=INFO
   ```

## Running the Application

1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python 03-direct-inference-sdk-chat-client/app.py
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

Logs are written to a `03-direct-inference-sdk-chat-client.log` file in the application directory to avoid polluting the chat output.

## Key Differences from Other Examples

This example differs from the other examples in the following ways:

1. **Direct Connection**: Instead of connecting through an Azure AI Foundry project, this example connects directly to an Azure AI Inference endpoint using an API key.

2. **Client Creation**: This example uses `ChatCompletionsClient` from the `azure.ai.inference` package with direct endpoint and API key:
   ```python
   chat_client = ChatCompletionsClient(
       endpoint=endpoint,
       credential=AzureKeyCredential(api_key)
   )
   ```

3. **API Usage**: This example uses a payload-based approach:
   ```python
   payload = {
       "messages": conversation_history,
       "max_tokens": 4096,
       "temperature": 0.7,
       "top_p": 1,
       "stop": []
   }
   response = chat_client.complete(payload)
   ```

4. **Authentication**: This example uses `AzureKeyCredential` with a direct API key instead of `DefaultAzureCredential` with a connection string.

This approach provides a more lightweight integration option when you don't need the full Azure AI Foundry project context and want to connect directly to an Azure AI Inference endpoint.
