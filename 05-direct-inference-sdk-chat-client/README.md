# Azure AI Inference SDK Chat Client Example

## Introduction
This is a simple example application demonstrating how to use the Azure AI Inference SDK to create a chat client that connects directly to an Azure AI Inference endpoint, sends message history to a language model, and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure AI Inference SDK**: Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, rather than through the Azure AI Foundry project client.

This example showcases:
- How to initialize the Azure AI Inference chat client directly
- How to authenticate using an API key
- How to send prompts and receive responses using the Azure AI Inference SDK
- How to maintain conversation context across multiple exchanges

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires the following specific environment variables setting in `.env`:
```
AZURE_INFERENCE_ENDPOINT=your-endpoint-url
AZURE_INFERENCE_API_KEY=your-api-key
```

## Running the Application
1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python 05-direct-inference-sdk-chat-client/app.py
   ```
3. Enter your questions when prompted
4. The application maintains conversation history for context, so follow-up questions work naturally
5. Type 'clear' to reset the conversation history
6. Type 'quit' to quit the application

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
