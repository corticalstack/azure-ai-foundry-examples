# Azure AI Agents with Semantic Kernel

This folder contains examples demonstrating how to create and use the AI agents servuce with Azure AI Foundry and Semantic Kernel.

## Examples Overview

| Example | Description |
|---------|-------------|
| [09_1_sk_simple_agent_chat.py](./09_1_sk_simple_agent_chat.py) | An interactive chat application with an Azure AI agent using Semantic Kernel. The application creates an agent, maintains a conversation thread, and provides a command-line interface for user interaction. |
| [09_2_sk_simple_agent_code_interpreter.py](./09_2_sk_simple_agent_code_interpreter.py) | Shows how to use code interpreter with Semantic Kernel to execute code and generate visualizations. The example uploads stock data and asks the agent to create a normalized stock price comparison chart. |
| [09_3_sk_simple_agent_file_search.py](./09_3_sk_simple_agent_file_search.py) | Demonstrates how to use agent operations with file searching orchestrated by Semantic Kernel. Searches through multiple uploaded documents to find relevant information and answer questions based on the content. |
| [09_4_sk_simple_agent_group_chat.py](./09_4_sk_simple_agent_group_chat.py) | Demonstrates a collaborative agent group chat system using Semantic Kernel. It involves two specialized AI agents: a Reviewer Agent that analyzes content and provides improvement suggestions, and a Writer Agent that rewrites content based on these suggestions. The conversation continues until the content is deemed satisfactory. |
| [09_5_sk_multi_agent_job_application_prep.ipynb](./09_5_sk_multi_agent_job_application_prep.ipynb) | Showcases a multi-agent system for job application preparation. It involves four specialized agents: Web-Job-Research-Agent, Resume-Reviewer-Agent, Resume-Copywriter-Agent, and Interview-Preparation-Agent. These agents collaborate to enhance a candidate's job application process, from resume tailoring to interview preparation. |

## Setup

### Environment Variables

Before running the examples, you need to set up the following environment variables in your `.env` file:

```
# Required for Azure AI agents with Semantic Kernel (examples 09_1 through 09_4)
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = "<your-project-connection-string>"
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = "<your-model-deployment-name>"

# Required for multi-agent job application prep (example 09_5)
AZURE_OPENAI_ENDPOINT = "<your-azure-openai-endpoint>"
AZURE_OPENAI_DEPLOYMENT = "<your-azure-openai-deployment-name>"
AZURE_OPENAI_API_KEY = "<your-azure-openai-api-key>"
APPLICATIONINSIGHTS_CONNECTION_STRING = "<your-application-insights-connection-string>"  # For telemetry
```

The project connection string follows this format: `<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<ProjectName>`. You can obtain these values from the Azure AI Foundry portal.
