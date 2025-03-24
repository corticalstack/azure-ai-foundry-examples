# Azure AI Inference SDK Prompty File Example

## Introduction
This is a simple example application demonstrating how to use the Azure AI Inference SDK with .prompty files. It shows how to load a prompt template, model name, and parameters from a .prompty file, populate template variables with values, and send the resulting messages to an Azure AI Inference endpoint for completion.

**Important distinction**: This example specifically demonstrates model consumption with the **Azure AI Inference SDK**: Models are consumed through a direct connection to an Azure AI Inference endpoint using an API key, rather than through the Azure AI Foundry project client.

This example showcases:
- How to initialize the Azure AI Inference chat client directly
- How to create and use prompt templates loaded from .prompty files
- How to extract model name and parameters from .prompty files
- How to pass variables to a template using mustache syntax (`{{variable_name}}`)
- How to send the generated messages to the model and receive a response

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires the following specific environment variables:
```
AZURE_INFERENCE_ENDPOINT=your-endpoint-url
AZURE_INFERENCE_API_KEY=your-api-key
```

## Running the Application
1. Make sure you've configured your `.env` file as described above
2. Run the application:
   ```bash
   python 09-direct-inference-with-prompty-file/app.py
   ```
3. The application will:
   - Load a prompt template from the writing_assistant.prompty file
   - Extract the model name and parameters from the .prompty file
   - Generate messages by filling in the template with values ("Jane" and "Doe")
   - Display the generated messages
   - Send the messages to the model using the extracted model name and parameters
   - Display the model's response

## Prompty Files
This example demonstrates how to use .prompty files to store prompt templates, model names, and parameters:

```
---
model: gpt-4
parameters:
  temperature: 0.7
  max_tokens: 4096
  top_p: 1.0
---

system:
You are a helpful writing assistant.
The user's first name is {{first_name}} and their last name is {{last_name}}.

user:
Write me a poem about flowers
```

The .prompty file format consists of:
1. A YAML section between `---` delimiters that contains:
   - `model`: The name of the model to use
   - `parameters`: A map of parameter names to values
2. The prompt template content with variables using mustache syntax (`{{variable_name}}`)

## Benefits of Prompty Files
Using .prompty files offers several advantages:
- **Separation of concerns**: Keep prompt templates separate from code
- **Reusability**: Use the same prompt template in multiple applications
- **Versioning**: Track changes to prompt templates in version control
- **Collaboration**: Share prompt templates with team members
- **Configuration**: Store model names and parameters alongside the prompt template
