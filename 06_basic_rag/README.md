# Basic RAG (Retrieval-Augmented Generation) example

## Introduction
This folder contains a Jupyter notebook that demonstrates a basic RAG implementation using Azure AI associated assets including text generation models and Azure AI Search. With a space facts theme 🚀 !

The example shows how to:

1. Connect to Azure AI Foundry using AIProjectClient
2. Create and test an instantiation to an embedding model
3. Connect to Azure AI Search
4. Create and populate a search index with sample space facts, with vector embeddings for each document content
5. Implement a RAG pattern for answering space-related questions

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