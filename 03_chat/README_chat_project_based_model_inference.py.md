# Project based Azure AI Model Inference Chat Client Example (Azure AI Service)

## Introduction
This is a simple example application demonstrating how to use the Azure AI Foundry Python SDK to create a chat completion client, where the application connects to the Azure AI Foundry project, sends message history to a language model (in this example, **gpt-4o-mini**, but this can be changed), and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with **Azure AI model inference** via the foundry project: A single endpoint for multiple models of different types, including OpenAI models and others from the Azure AI Foundry model catalog. Models are consumed through an Azure AI services resource connection in the project, rather than a model deployed to an Azure OpenAI service.

This example showcases:
- How to initialize the Azure AI Foundry project client
- How to create a chat completions client for Azure AI model inference
- How to send prompts and receive responses
- How to implement tracing to monitor and log the AI model's performance, usage patterns, and content generation

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
