# Azure AI Agents with Semantic Kernel

This folder contains examples demonstrating how to create and use the AI agents servuce with Azure AI Foundry and Semantic Kernel.

## Examples Overview

| Example | Description |
|---------|-------------|
| [09_1_sk_simple_agent_chat.py](./09_1_sk_simple_agent_chat.py) | An interactive chat application with an Azure AI agent using Semantic Kernel. The application creates an agent, maintains a conversation thread, and provides a command-line interface for user interaction. |
| [09_2_sk_simple_agent_code_interpreter.py](./09_2_sk_simple_agent_code_interpreter.py) | Shows how to use code interpreter with Semantic Kernel to execute code and generate visualizations. The example uploads stock data and asks the agent to create a normalized stock price comparison chart. |
| [09_3_sk_simple_agent_file_search.py](./09_3_sk_simple_agent_file_search.py) | Demonstrates how to use agent operations with file searching orchestrated by Semantic Kernel. Searches through multiple uploaded documents to find relevant information and answer questions based on the content. |

## Setup and Configuration

### Prerequisites

1. An Azure account with an active subscription
2. Azure AI Foundry project with Azure AI agents enabled
3. Python 3.8 or later
4. Semantic Kernel library with Azure dependencies

### Installation

Install the required dependencies:

```bash
pip install semantic-kernel[azure]
```

### Environment Variables

Before running the examples, you need to set up the following environment variables in your `.env` file:

```
# Required for Azure AI agents with Semantic Kernel
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = "<your-project-connection-string>"
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = "<your-model-deployment-name>"
```

The project connection string follows this format: `<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<ProjectName>`. You can obtain these values from the Azure AI Foundry portal.

## Running the Examples

1. Make sure you've configured your `.env` file as described above
2. Run the desired example:
   ```bash
   python 09_agents_with_semantic_kernel/09_1_sk_simple_agent_chat.py
   ```