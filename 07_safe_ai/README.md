# Safe AI - Content Moderation Example

## Introduction
This folder contains a Jupyter notebook that demonstrates how to use Azure Content Safety to moderate text content. The example provides interactive widgets to adjust moderation settings and test different text inputs.

The example shows how to:

1. Connect to Azure AI Services for content moderation
2. Define content categories for moderation (*Hate*, *Self Harm*, *Sexual*, *Violence*)
3. Set up threshold values for different content categories
4. Analyze text content for potentially harmful material
5. Make accept/reject decisions based on moderation results
6. Visualize and understand content moderation results

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires setting the following specific environment variables in `.env`:
```
AZURE_AI_SERVICES_ENDPOINT=your-ai-services-endpoint
AZURE_AI_SERVICES_API_KEY=your-ai-services-api-key
```

You can find these values in the Azure AI Foundry portal:
1. Go to your Azure AI Foundry resource
2. Navigate to the Management Center
3. Go to Connected Resources
4. Select your AIServices resource
5. Copy the target endpoint URL and API key