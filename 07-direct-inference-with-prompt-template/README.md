# Azure AI Inference SDK Prompt Template Example

## Introduction
This is a simple example application demonstrating how to use the Azure AI Inference SDK with prompt templates. It shows how to create a prompt template with variables, populate those variables with values, and send the resulting messages to an Azure AI Inference endpoint for completion.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure AI Inference SDK**: Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, rather than through the Azure AI Foundry project client.

This example showcases:
- How to initialize the Azure AI Inference chat client directly
- How to create and use prompt templates with the `PromptTemplate` class
- How to pass variables to a template using mustache syntax (`{{variable_name}}`)
- How to send the generated messages to the model and receive a response

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
   python 07-direct-inference-with-prompt-template/app.py
   ```
3. The application will:
   - Create a prompt template with variables for first_name and last_name
   - Generate messages by filling in the template with values
   - Display the generated messages
   - Send the messages to the model
   - Display the model's response

## Prompt Templates

This example demonstrates how to use the `PromptTemplate` class from the Azure AI Inference SDK to create templates with variables:

```python
from azure.ai.inference.prompts import PromptTemplate

# Create a prompt template with variables using mustache syntax
prompt_template = PromptTemplate.from_string(prompt_template="""
system:
You are a helpful writing assistant.
The user's first name is {{first_name}} and their last name is {{last_name}}.

user:
Write me a poem about flowers
""")

# Generate messages by filling in the template variables
messages = prompt_template.create_messages(first_name="Jane", last_name="Doe")
```
