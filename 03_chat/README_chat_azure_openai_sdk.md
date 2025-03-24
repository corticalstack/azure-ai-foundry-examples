# Azure OpenAI SDK Chat Client Example

## Introduction
This is a simple example application demonstrating how to use the Azure OpenAI SDK to create a chat client that connects directly to an Azure OpenAI endpoint deployed , sends message history to a language model, and displays the response.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure OpenAI SDK**: Models are consumed through a direct connection to an Azure OpenAI endpoint using an API key, rather than through the Azure AI Foundry project client. Here you use the Azure OPenAI SDK.

This example showcases:
- How to initialize the Azure OpenAI chat client directly
- How to authenticate using an API key
- How to send prompts and receive responses using the Azure OpenAI SDK
- How to maintain conversation context across multiple exchanges

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires the following specific environment variables:
```
AZURE_INFERENCE_ENDPOINT=your-endpoint-url
AZURE_INFERENCE_API_KEY=your-api-key
```

Note: The endpoint URL should include the deployment name, e.g., `https://<resource-name>.openai.azure.com/openai/deployments/<deployment-name>/`

## Running the Application
1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python 05-azure-openai-sdk-chat-client/app.py
   ```
3. Enter your questions when prompted
4. The application maintains conversation history for context, so follow-up questions work naturally
5. Type 'clear' to reset the conversation history
6. Type 'quit' to quit the application

## Key Differences from Other Examples
This example differs from the other examples in the following ways:

1. **Direct Connection**: Instead of connecting through an Azure AI Foundry project, this example connects directly to an Azure OpenAI endpoint using an API key.

2. **Client Creation**: This example uses `AzureOpenAI` from the `openai` package with direct endpoint and API key:
   ```python
   chat_client = AzureOpenAI(
       api_key=api_key,
       api_version="<api version>",
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
