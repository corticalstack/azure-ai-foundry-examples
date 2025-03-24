# Azure AI Foundry Chat with Prompt Templates Examples

This folder contains examples demonstrating how to use prompt templates with Azure AI Foundry model services.

## Examples Overview

| Example | Description |
|---------|-------------|
| [chat_direct_inference_with_prompt_template.py](./chat_direct_inference_with_prompt_template.py) | Uses Azure AI Inference SDK with prompt templates created programmatically |
| [chat_direct_inference_with_prompty_file.py](./chat_direct_inference_with_prompty_file.py) | Uses Azure AI Inference SDK with prompt templates loaded from .prompty files |

## Detailed Descriptions

### Direct Inference with Prompt Template

**File**: [chat_direct_inference_with_prompt_template.py](./chat_direct_inference_with_prompt_template.py)

This example demonstrates how to use the Azure AI Inference SDK with prompt templates. It shows how to create a prompt template with variable placeholders, populate those placeholders with values, and send the resulting messages to an Azure AI Inference endpoint for completion.

Key features:
- Creates and uses prompt templates with the `PromptTemplate` class
- Passes variables to a template using mustache syntax (`{{variable_name}}`)

Example of creating a prompt template programmatically:

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

### Direct Inference with Prompty File

**File**: [chat_direct_inference_with_prompty_file.py](./chat_direct_inference_with_prompty_file.py)

This example demonstrates how to use the Azure AI Inference SDK with .prompty files. It shows how to load a prompt template, model name, and parameters from a .prompty file, populate template variable placeholders with values, and send the resulting messages to an Azure AI Inference endpoint for completion.

Key features:
- Creates and uses prompt templates loaded from .prompty files
- Extracts model name and parameters from .prompty files
- Passes variables to a template using mustache syntax (`{{variable_name}}`)

Example of a .prompty file format:

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

## Benefits of Prompt Templates

Using prompt templates offers several advantages:
- **Reusability**: Reuse the same template with different variable values
- **Separation of concerns**: Keep prompt templates separate from code
- **Versioning**: Track changes to prompt templates in version control
- **Collaboration**: Share prompt templates with team members

## Setup and Configuration

For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

### Example-Specific Requirements

These examples require the following specific environment variables:
```
AZURE_INFERENCE_ENDPOINT=your-endpoint-url
AZURE_INFERENCE_API_KEY=your-api-key
```

## Running the Applications

1. Make sure you've configured your `.env` file as described above
2. Run the desired application:
   ```bash
   python 04_chat_with_prompt_templates/[example_file].py
   ```
3. The application will:
   - Create or load a prompt template
   - Generate messages by filling in the template variable placeholders with values
   - Display the generated messages
   - Send the messages to the model
   - Display the model's response
