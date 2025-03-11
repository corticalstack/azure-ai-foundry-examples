# Azure AI Model Inference Chat Client Example (Azure AI Service)

## Introduction

This is a simple example application demonstrating how to use the Azure AI Foundry Python SDK to create a chat completion client, where the application connects to the Azure AI Foundry project, sends message history to a language model (in this example, **gpt-4o-mini**, but this can be changed), and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with **Azure AI model inference**: A single endpoint for multiple models of different types, including OpenAI models and others from the Azure AI Foundry model catalog. Models are consumed through an Azure AI services resource connection in the project, rather than a model deployed to an Azure OpenAI service.

This example showcases:
- How to initialize the Azure AI Foundry project client
- How to create a chat completions client for Azure AI model inference
- How to send prompts and receive responses

## Setup Guide

### Prerequisites

- Azure account with access to Azure AI Foundry
- Azure AI Foundry project created
- VS Code with Dev Containers extension installed
- Docker installed on your system

### Project Connection String

To use this client, you need to set up a project connection string in the following format:
```
<region>.api.azureml.ms;<project_id>;<hub_name>;<project_name>
```

You can find these values in the Azure AI Foundry portal:
1. Go to your project in the Azure AI Foundry portal
2. Click on 'Project settings'
3. Look for the project connection string information

### Using Dev Container

This project includes a development container configuration that sets up all necessary dependencies automatically.

To launch the dev container:

1. Open the project folder in VS Code
2. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev Containers: Reopen in Container"
3. VS Code will build the container and set up the environment (this may take a few minutes the first time)
4. Once the container is running, you'll have a fully configured environment with all dependencies installed
5. The dev container includes the Azure CLI. Run `az login` to authenticate with your Azure account before running the application

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

3. Make sure you're authenticated with Azure:
   ```bash
   az login
   ```

## Environment Configuration

The application uses environment variables for configuration, which are loaded from a `.env` file:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and replace the placeholder connection string with your actual Azure AI Foundry project connection string:
   ```
   AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING=your-actual-connection-string
   ```

3. Optionally, adjust the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL):
   ```
   LOG_LEVEL=INFO
   ```

## Running the Application

1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python app.py
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

Logs are written to a `chat_client.log` file in the application directory to avoid polluting the chat output.