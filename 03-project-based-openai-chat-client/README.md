# Project based Azure OpenAI Chat Client Example (Azure OpenAI Service)

## Introduction
This is a simple example application demonstrating how to use the Azure AI Foundry Python SDK to create an Azure OpenAI client, where the application connects to the Azure AI Foundry project, sends message history to a language model deployed to Azure OpenAI service, and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with **Azure OpenAI service**: Models are consumed through an Azure OpenAI service resource connection in the project, rather than through the Azure AI model inference service.

This example showcases:
- How to initialize the Azure AI Foundry project client
- How to create an Azure OpenAI client using the project connection
- How to send prompts and receive responses using the Azure AI projects AIProjectClient object

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires setting the following specific environment variable in `.env`:
```
AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING=your-actual-connection-string
```

You can this in the Azure AI Foundry portal:
1. Go to your project in the Azure AI Foundry portal
2. Click on 'Project settings'
3. Look for the project connection string information

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