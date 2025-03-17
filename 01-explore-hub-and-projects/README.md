# Explore Azure AI Foundry Hub and Projects

This example demonstrates how to explore and interact with the Azure AI Foundry hub and associated projects, connections, and cognitive services using various SDKs.

## Overview

Explores:

- Retrieving and displaying detailed information about your AI Foundry hub
- Understanding hub and project concepts through class documentation
- Listing and exploring all child projects associated with your hub
- Examining hub and project connections
- Viewing project service deployments and cognitive services

## Prerequisites

To run this notebook, you'll need:

1. An Azure AI Foundry hub with associated projects
2. Proper authentication credentials (using DefaultAzureCredential)
3. Environment variables configured in a `.env` file:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `AZURE_AI_FOUNDRY_HUB_NAME`

## Usage

1. Ensure your environment variables are properly set in the `.env` file
2. Open the notebook in a Jupyter environment
3. Run the cells sequentially to explore your Azure AI Foundry environment