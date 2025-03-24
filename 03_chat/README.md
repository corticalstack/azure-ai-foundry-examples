# Azure AI Foundry Chat Examples

This folder contains examples demonstrating different ways to create chat applications using Azure AI Foundry services. Each example showcases a different approach to connecting to and consuming model assets for chat completions.

## Examples Overview

| Example | Description |
|---------|-------------|
| [chat_project_based_model_inference.py](./chat_project_based_model_inference.py) | Uses Azure AI Foundry Python SDK to create a chat completion client via a foundry project for Azure AI model inference |
| [chat_project_based_openai.py](./chat_project_based_openai.py) | Uses Azure AI Foundry Python SDK to create an Azure OpenAI client via a foundry project |
| [chat_azure_openai_sdk.py](./chat_azure_openai_sdk.py) | Uses Azure OpenAI SDK to directly connect to a foundry-deployed Azure OpenAI endpoint using an API key |
| [chat_direct_inference_sdk.py](./chat_direct_inference_sdk.py) | Uses Azure AI Inference SDK to directly connect to an Azure AI Inference endpoint using an API key |
| [chat_direct_inference_sdk_streaming.py](./chat_direct_inference_sdk_streaming.py) | Uses Azure AI Inference SDK with asynchronous streaming responses |

## Detailed Descriptions

### Project-based Model Inference Chat Client

**Code**: [chat_project_based_model_inference.py](./chat_project_based_model_inference.py)

This example demonstrates model consumption with **Azure AI model inference** via the foundry project. It uses a single endpoint for multiple models of different types, including OpenAI models and others from the Azure AI Foundry model catalog. Models are consumed through an Azure AI services resource connection in the project.

Key features:
- Initializes the Azure AI Foundry project client
- Creates a chat completions client for Azure AI model inference
- Implements tracing to monitor and log the AI model's performance

### Project-based OpenAI Chat Client

**Code**: [chat_project_based_openai.py](./chat_project_based_openai.py)

This example demonstrates model consumption with **Azure OpenAI service**. Models are consumed through an Azure OpenAI service resource connection in the project, rather than through the Azure AI model inference service.

Key features:
- Initializes the Azure AI Foundry project client
- Creates an Azure OpenAI client using the project connection
- Sends prompts and receives responses using the Azure AI projects AIProjectClient object

### Azure OpenAI SDK Chat Client

**Code**: [chat_azure_openai_sdk.py](./chat_azure_openai_sdk.py)

This example demonstrates model consumption with the well-known **Azure OpenAI SDK**. Models are consumed through a direct connection to an Azure OpenAI endpoint using an API key, rather than through the Azure AI Foundry project client.

Key features:
- Initializes the Azure OpenAI chat client directly
- Authenticates using an API key
- Sends prompts and receives responses using the Azure OpenAI SDK

### Direct Inference SDK Chat Client

**Code**: [chat_direct_inference_sdk.py](./chat_direct_inference_sdk.py)

This example demonstrates model consumption with the **Azure AI Inference SDK**. Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, rather than through the Azure AI Foundry project client.

Key features:
- Initializes the Azure AI Inference chat client directly
- Authenticates using an API key
- Sends prompts and receives responses using the Azure AI Inference SDK

### Direct Inference SDK Streaming Chat Client

**Code**: [chat_direct_inference_sdk_streaming.py](./chat_direct_inference_sdk_streaming.py)

This example demonstrates model consumption with the **Azure AI Inference SDK** using **streaming responses**. Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, with responses streamed back and displayed in real-time as they are generated.

Key features:
- Uses Python's `asyncio` to handle asynchronous operations
- Enables streaming by setting `stream=True` in the *client.complete* call
- Processes response chunks as they arrive using a helper function
- Shows response tokens in real-time as they are generated
- Accumulates the complete response for conversation history

## Setup and Configuration

For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

### Example-Specific Requirements

#### For Project-based Examples
These examples require setting the following specific environment variable in `.env`:
```
AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING=your-actual-connection-string
```

You can find this in the Azure AI Foundry portal:
1. Go to your project in the Azure AI Foundry portal
2. Click on 'Project settings'
3. Look for the project connection string information

#### For Direct Connection Examples
These examples require the following specific environment variables:
```
AZURE_INFERENCE_ENDPOINT=your-endpoint-url
AZURE_INFERENCE_API_KEY=your-api-key
```

## Running the Applications

1. Make sure you've configured your `.env` file as described above
2. Run the desired application:
   ```bash
   python 03_chat/[example_file].py
   ```
3. Enter your questions when prompted
4. The applications maintain conversation history for context, so follow-up questions work naturally
5. Type *clear* to reset the conversation history
6. Type *quit* to quit the application
