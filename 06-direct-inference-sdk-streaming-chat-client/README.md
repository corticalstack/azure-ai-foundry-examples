# Azure AI Inference SDK Streaming Chat Client Example (06)

## Introduction
This is a simple example application demonstrating how to use the Azure AI Inference SDK to create a chat client that connects directly to an Azure AI Inference endpoint, sends message history to a language model, and displays the response using **asynchronous streaming**.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure AI Inference SDK** using **streaming responses**: Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, with responses streamed back in real-time as they are generated.

## Key Streaming Features
This example differs from the non-streaming example (05-direct-inference-sdk-chat-client) in the following ways:

1. **Asynchronous Code**: Uses Python's `asyncio` to handle asynchronous operations
2. **Streaming Responses**: Enables streaming by setting `stream=True` in the client.complete call
3. **Chunk Processing**: Processes response chunks as they arrive using a helper function
4. **Real-time Display**: Shows response tokens in real-time as they are generated
5. **Full Response Collection**: Accumulates the complete response for conversation history

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
   python 06-direct-inference-sdk-streaming-chat-client/app.py
   ```
3. Enter your questions when prompted
4. Watch as the response is streamed back in real-time, token by token
5. The application maintains conversation history for context, so follow-up questions work naturally
6. Type 'clear' to reset the conversation history
7. Type 'quit' to quit the application
