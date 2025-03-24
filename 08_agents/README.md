# Azure AI Foundry Agents Examples

This folder contains examples demonstrating how to create and use AI agents with Azure AI Foundry. Each example showcases a different capability or integration with Azure AI agents.

## Examples Overview

| Example | Description |
|---------|-------------|
| [08_1_simple_agent_personal_learning_coach_azure_monitor_tracing.ipynb](./08_1_simple_agent_personal_learning_coach_azure_monitor_tracing.ipynb) | Demonstrates a personal learning coach agent with Azure Monitor tracing |
| [08_2_simple_agent_bing_grounding.py](./08_2_simple_agent_bing_grounding.py) | Shows how to create an agent with Bing grounding for factual responses |
| [08_3_simple_agent_code_interpreter.py](./08_3_simple_agent_code_interpreter.py) | Implements an agent with code generation capabilities |
| [08_4_simple_agent_file_search.py](./08_4_simple_agent_file_search.py) | Creates an agent that can search through multiple files for information |
| [08_5_simple_agent_functions.py](./08_5_simple_agent_functions.py) | Demonstrates an agent that can call appropriate external functions for best conversational response|

## Additional Resources

Many more Azure AI Agent examples can be found in this [GitHub repo](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)

## Setup and Configuration

For detailed setup instructions including prerequisites, dev container usage, manual setup, and general environment configuration, please refer to the [main README](../README.md#%EF%B8%8F-setup-guide).

### Example-Specific Requirements

These examples may require specific environment variables or dependencies. Please refer to the individual example files for specific requirements.

## Running the Applications

1. Make sure you've configured your `.env` file as described in the main README
2. Run the desired application:
   ```bash
   python 08_agents/[example_file].py
   ```
   or open the notebook in a Jupyter environment:
   ```bash
   jupyter notebook 08_agents/[example_file].ipynb
   ```
