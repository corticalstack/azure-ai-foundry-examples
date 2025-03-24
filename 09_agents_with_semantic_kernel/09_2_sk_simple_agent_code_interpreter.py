"""
Azure AI Agent Code Interpreter with Semantic Kernel Example

This sample demonstrates how to use code interpreter with Semantic Kernel to execute code 
and generate visualizations. The example uploads stock data and asks the agent to create 
a normalized stock price comparison chart.

Note: Code interpreter works with the following Azure OpenAI models:
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo
- gpt-4o

For more information, see: 
https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/code-interpreter

Be aware, if you consistently get retry failures, double-check the Tokens Per Minute (TPM) 
limit set against your AI Foundry model deployment.
"""

import asyncio
import pathlib
from typing import Any, List, Tuple

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose
from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents.azure_ai import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole

DATA_FILE_PATH = pathlib.Path(__file__).parent.parent / "assets" / "data" / "stockdata.csv"

# The task for the agent to perform
TASK = """Plot a line chart showing the stock prices for 2013 for MSFT, IBM, SBUX, AAPL, and GSPC from the uploaded csv file.
Normalize all stock prices to show percentage change relative to their initial value so they can be directly compared on the same scale.
Save the plot as a file for me"""


async def initialize_agent_settings() -> AzureAIAgentSettings:
    """
    Initialize and return the Azure AI agent settings.
    
    Returns:
        AzureAIAgentSettings: Configured settings for the Azure AI agent.
    """
    return AzureAIAgentSettings.create()  # Note the variable configuration prerequisites in your .env


async def create_agent_client(credential: DefaultAzureCredential) -> AIProjectClient:
    """
    Create and return an Azure AI agent client.
    
    Args:
        credential (DefaultAzureCredential): Azure credential for authentication.
        
    Returns:
        AIProjectClient: Client for interacting with Azure AI agent service.
    """
    return AzureAIAgent.create_client(credential=credential)


async def upload_data_file(client: AIProjectClient, file_path: pathlib.Path):
    """
    Upload a data file for the code interpreter to use.
    
    Args:
        client (AIProjectClient): Client for interacting with Azure AI agent service.
        file_path (pathlib.Path): Path to the file to upload.
        
    Returns:
        FileReference: Reference to the uploaded file.
    """
    file = await client.agents.upload_file_and_poll(
        file_path=file_path, purpose=FilePurpose.AGENTS
    )
    print(f"Uploaded file, file ID: {file.id}")
    return file


async def setup_agent_with_code_interpreter(
    client: AIProjectClient,
    settings: AzureAIAgentSettings,
    file_ids: List[str]
) -> Tuple[AzureAIAgent, Any]:
    """
    Set up an Azure AI agent with code interpreter capability and create a conversation thread.
    
    Args:
        client (AIProjectClient): Client for interacting with Azure AI agent service.
        settings (AzureAIAgentSettings): Configured settings for the Azure AI agent.
        file_ids (List[str]): List of file IDs to make available to the code interpreter.
        
    Returns:
        Tuple[AzureAIAgent, Thread]: The created agent and conversation thread.
    """
    # Create a code interpreter tool with the uploaded file
    code_interpreter = CodeInterpreterTool(file_ids=file_ids)
    
    # Create an agent with the code interpreter on the Azure AI agent service
    agent_definition = await client.agents.create_agent(
        model=settings.model_deployment_name,
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    print(f"Created agent, agent ID: {agent_definition.id}")
    
    # Create a Semantic Kernel agent for the Azure AI agent
    agent = AzureAIAgent(
        client=client,
        definition=agent_definition,
    )
    
    thread = await client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")
    
    return agent, thread


async def process_task(
    agent: AzureAIAgent,
    thread_id: str,
    task: str
) -> None:
    """
    Process a task by sending it to the agent and displaying the response.
    
    Args:
        agent (AzureAIAgent): The Azure AI agent.
        thread_id (str): ID of the conversation thread.
        task (str): The task for the agent to perform.
    """
    await agent.add_chat_message(thread_id=thread_id, message=task)
    print(f"# User: '{task}'")
    
    # Invoke the agent for the specified thread for response
    # We filter out tool messages as they contain internal execution details
    async for content in agent.invoke(thread_id=thread_id):
        if content.role != AuthorRole.TOOL:
            print(f"# Agent: {content.content}")


async def save_generated_files(
    client: AIProjectClient,
    thread_id: str,
    output_dir: pathlib.Path
) -> None:
    """
    Save any files generated by the code interpreter.
    
    Args:
        client (AIProjectClient): Client for interacting with Azure AI agent service.
        thread_id (str): ID of the conversation thread.
        output_dir (pathlib.Path): Directory to save the generated files.
    """
    messages = await client.agents.list_messages(thread_id=thread_id)
    
    for file_path_annotation in messages.file_path_annotations:
        file_id = file_path_annotation.file_path.file_id
        file_name = f"{file_id}_normalized_stock_prices.png"
        file_path = output_dir / file_name
        await client.agents.save_file(file_id=file_id, file_name=str(file_path))
        print(f"Saved plot to: {file_path}")


async def cleanup_resources(
    client: AIProjectClient,
    thread_id: str,
    agent_id: str,
    file_id: str
) -> None:
    """
    Clean up resources by deleting the thread, agent, and uploaded file.
    
    Args:
        client (AIProjectClient): Client for interacting with Azure AI agent service.
        thread_id (str): ID of the thread to delete.
        agent_id (str): ID of the agent to delete.
        file_id (str): ID of the file to delete.
    """
    await client.agents.delete_thread(thread_id)
    await client.agents.delete_agent(agent_id)
    await client.agents.delete_file(file_id)
    print("Cleaned up resources (thread, agent, and file)")


async def main() -> None:
    """
    Main function that orchestrates the Azure AI agent code interpreter example.
    """
    ai_agent_settings = await initialize_agent_settings()

    async with DefaultAzureCredential() as creds, \
               await create_agent_client(creds) as client:
        
        file = await upload_data_file(client, DATA_FILE_PATH)
        
        agent, thread = await setup_agent_with_code_interpreter(
            client, 
            ai_agent_settings, 
            [file.id]
        )
        
        try:
            await process_task(agent, thread.id, TASK)
            
            script_dir = pathlib.Path(__file__).parent.absolute()
            await save_generated_files(client, thread.id, script_dir)
            
        finally:
            await cleanup_resources(client, thread.id, agent.id, file.id)


if __name__ == "__main__":
    asyncio.run(main())
