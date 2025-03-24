# Azure AI Search Index Example

## Introduction
This example demonstrates how to use Azure AI Search with an Azure AI Foundry project. It shows how to create a search index, upload documents, and perform search operations using a Jupyter notebook.

The example specifically focuses on:
- Connecting to the default AI Search service in an AI Foundry project
- Creating a custom index with a defined schema
- Uploading sample data to the index
- Performing various search operations

## Setup and Configuration
For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

## Example-Specific Requirements
This example requires setting the following specific environment variable in `.env`:
```
AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING=your-actual-connection-string
```

You can find this in the Azure AI Foundry portal:
1. Go to your project in the Azure AI Foundry portal
2. Click on *Project settings*
3. Look for the project connection string information