"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with file searching using Semantic Kernel.

    Searches through multiple uploaded documents to find relevant information and answer questions based on the content.

USAGE:
    Set these environment variables with your own values in your .env file:
    
    - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint
    - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
    - AZURE_OPENAI_DEPLOYMENT_NAME: Your Azure OpenAI model deployment name
    
    Command-line arguments:
    
    - --query N: Run a specific test query (N is a number from 1 to 4)
    - --custom-query "Your query here": Run a custom query instead of the predefined test queries
    - --list-queries: List all available test queries and exit
    
    Examples:
    
    python 09_3_sk_simple_agent_file_search.py                                  # Run all test queries
    python 09_3_sk_simple_agent_file_search.py --query 2                        # Run only the second test query
    python 09_3_sk_simple_agent_file_search.py --list-queries                   # List all available test queries
    python 09_3_sk_simple_agent_file_search.py --custom-query "Tell me about SmartView Glasses warranty"  # Run a custom query

Note: File search works with the following Azure OpenAI models:
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo
- gpt-4o

For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/file-search
"""

import asyncio
import argparse
import os
import pathlib
import sys
from typing import Any, List, Optional, Tuple

from azure.ai.projects.models import FileSearchTool, OpenAIFile, VectorStore
from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents.azure_ai import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents import AuthorRole

# Sample queries to demonstrate capabilities across one or more source documents
DEFAULT_USER_QUERIES = [
    "Tell me about all Contoso products you know about and compare their features, warranty, and return policies.",
    "What are the features of the SmartView Glasses?",
    "Tell me about the SmartHub Control Center.",
    "Compare the warranty periods of all Contoso products."
]

# List of product info files to upload
PRODUCT_INFO_FILE_PATHS = [
    pathlib.Path(__file__).parent.parent / "assets/data/product_info_1.md",
    pathlib.Path(__file__).parent.parent / "assets/data/product_info_2.md",
]

# Agent instructions for the file search tool
AGENT_INSTRUCTIONS = """You are a helpful assistant that can search information from uploaded files. 
You have access to multiple product information files from Contoso. 
When asked about Contoso products, provide comprehensive information and compare products when appropriate, 
citing the specific files you're retrieving information from."""


async def initialize_agent_settings() -> AzureAIAgentSettings:
    """
    Initialize and return the Azure AI agent settings.
    
    Returns:
        AzureAIAgentSettings: Configured settings for the Azure AI agent.
    """
    return AzureAIAgentSettings.create()  # Note the variable configuration prerequisites in your .env


async def upload_file(client: Any, file_path: pathlib.Path) -> OpenAIFile:
    """
    Upload a file to the Azure AI agent service for file search.
    
    Args:
        client: Client for interacting with Azure AI agent service.
        file_path: Path to the file to upload.
        
    Returns:
        OpenAIFile: Reference to the uploaded file.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: For other upload errors.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        file = await client.agents.upload_file_and_poll(
            file_path=file_path, purpose="assistants"
        )
        print(f"Uploaded file, file ID: {file.id}")
        return file
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise


async def create_vector_store(client: Any, file_ids: List[str]) -> VectorStore:
    """
    Create a vector store from the uploaded files for efficient searching.
    
    Args:
        client: Client for interacting with Azure AI agent service.
        file_ids: List of file IDs to include in the vector store.
        
    Returns:
        VectorStore: The created vector store.
        
    Raises:
        ValueError: If file_ids is empty.
        Exception: For other vector store creation errors.
    """
    if not file_ids:
        raise ValueError("No file IDs provided for vector store creation")
        
    try:
        vector_store = await client.agents.create_vector_store_and_poll(
            file_ids=file_ids, name="my_vectorstore"
        )
        print(f"Created vector store, vector store ID: {vector_store.id}")
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        raise


async def setup_agent_with_file_search(
    client: Any,
    settings: AzureAIAgentSettings,
    vector_store_ids: List[str]
) -> Tuple[AzureAIAgent, Any]:
    """
    Set up an Azure AI agent with file search capability and create a conversation thread.
    
    Args:
        client: Client for interacting with Azure AI agent service.
        settings: Configured settings for the Azure AI agent.
        vector_store_ids: List of vector store IDs to make available to the file search tool.
        
    Returns:
        Tuple[AzureAIAgent, Thread]: The created agent and conversation thread.
        
    Raises:
        ValueError: If vector_store_ids is empty.
        Exception: For other agent creation errors.
    """
    if not vector_store_ids:
        raise ValueError("No vector store IDs provided for agent creation")
        
    try:
        # Create a file search tool with the vector store
        file_search = FileSearchTool(vector_store_ids=vector_store_ids)
        
        # Create an agent with the file search tool on the Azure AI agent service
        agent_definition = await client.agents.create_agent(
            model=settings.model_deployment_name,
            tools=file_search.definitions,
            tool_resources=file_search.resources,
            instructions=AGENT_INSTRUCTIONS
        )
        print(f"Created agent, agent ID: {agent_definition.id}")
        
        # Create a Semantic Kernel agent for the Azure AI agent
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )
        
        # Create a new thread for the conversation
        thread = await client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")
        
        return agent, thread
    except Exception as e:
        print(f"Error setting up agent: {e}")
        raise


async def process_query(
    agent: AzureAIAgent,
    thread_id: str,
    query: str
) -> None:
    """
    Process a user query by sending it to the agent and displaying the response.
    
    Args:
        agent (AzureAIAgent): The Azure AI agent.
        thread_id (str): ID of the conversation thread.
        query (str): The user query to process.
        
    Raises:
        Exception: If there's an error processing the query.
    """
    try:
        await agent.add_chat_message(thread_id=thread_id, message=query)
        print(f"\nUser Query:")
        print(query)
        
        # Invoke the agent for the specified thread for response
        # We filter out tool messages as they contain internal execution details
        print(f"Agent is thinking...")
        response_received = False
        
        async for content in agent.invoke(thread_id=thread_id):
            if content.role != AuthorRole.TOOL:
                response_received = True
                print(f"\nAgent Response:")
                print(content.content)
        
        if not response_received:
            print(f"No response received from agent")
            
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise


async def cleanup_resources(
    client: Any,
    thread_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    vector_store_id: Optional[str] = None,
    file_ids: Optional[List[str]] = None
) -> None:
    """
    Clean up resources by deleting the thread, agent, vector store, and uploaded files.
    Handles each deletion separately to ensure all resources are cleaned up even if some deletions fail.
    
    Args:
        client: Client for interacting with Azure AI agent service.
        thread_id (Optional[str]): ID of the thread to delete.
        agent_id (Optional[str]): ID of the agent to delete.
        vector_store_id (Optional[str]): ID of the vector store to delete.
        file_ids (Optional[List[str]]): List of file IDs to delete.
    """
    print("\nCleaning up resources...")
    
    if thread_id:
        try:
            await client.agents.delete_thread(thread_id)
            print(f"Deleted thread: {thread_id}")
        except Exception as e:
            print(f"Error deleting thread {thread_id}: {str(e)}")
    
    if agent_id:
        try:
            await client.agents.delete_agent(agent_id)
            print(f"Deleted agent: {agent_id}")
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {str(e)}")
    
    if vector_store_id:
        try:
            await client.agents.delete_vector_store(vector_store_id)
            print(f"Deleted vector store: {vector_store_id}")
        except Exception as e:
            print(f"Error deleting vector store {vector_store_id}: {str(e)}")
    
    if file_ids:
        for file_id in file_ids:
            try:
                await client.agents.delete_file(file_id)
                print(f"Deleted file: {file_id}")
            except Exception as e:
                print(f"Error deleting file {file_id}: {str(e)}")


async def run_queries(
    agent: AzureAIAgent,
    thread_id: str,
    queries: List[str]
) -> None:
    """
    Run a list of queries against the agent.
    
    Args:
        agent (AzureAIAgent): The Azure AI agent.
        thread_id (str): ID of the conversation thread.
        queries (List[str]): List of queries to process.
    """
    for i, query in enumerate(queries):
        print(f"\n{'='*80}")
        print(f"Running query {i+1}/{len(queries)}:")
        print(query)
        print(f"{'='*80}")
        
        try:
            await process_query(agent, thread_id, query)
        except Exception as e:
            print(f"Failed to process query: {query}")
            print(f"Error: {str(e)}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the file search agent.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run file search agent with Semantic Kernel")
    
    # Add query selection argument
    parser.add_argument(
        "--query", 
        type=int, 
        choices=range(1, len(DEFAULT_USER_QUERIES) + 1),
        help=f"Select a specific query to run (1-{len(DEFAULT_USER_QUERIES)}). If not provided, all queries will be run."
    )
    
    # Add custom query argument
    parser.add_argument(
        "--custom-query", 
        type=str,
        help="Run a custom query instead of the predefined test queries"
    )
    
    # Add list queries argument
    parser.add_argument(
        "--list-queries", 
        action="store_true",
        help="List all available test queries and exit"
    )
    
    return parser.parse_args()


async def main() -> None:
    """
    Main function that orchestrates the Azure AI agent file search example.
    """
    args = parse_arguments()
    
    # List queries if requested
    if args.list_queries:
        print("\nAvailable test queries:")
        for i, query in enumerate(DEFAULT_USER_QUERIES):
            print(f"{i+1}. {query}")
        return
    
    # Determine which queries to run
    queries_to_run = []
    if args.custom_query:
        queries_to_run = [args.custom_query]
        print(f"\nRunning custom query: {args.custom_query}")
    elif args.query:
        query_index = args.query - 1  # Convert to 0-based index
        queries_to_run = [DEFAULT_USER_QUERIES[query_index]]
        print(f"\nRunning test query {args.query}: {queries_to_run[0]}")
    else:
        queries_to_run = DEFAULT_USER_QUERIES
        print(f"\nRunning all {len(DEFAULT_USER_QUERIES)} test queries")
    
    # Initialize variables for resource cleanup
    file_ids = []
    vector_store_id = None
    agent_id = None
    thread_id = None
    
    try:
        # Initialize agent settings
        ai_agent_settings = await initialize_agent_settings()
        print("Initialized agent settings")

        async with DefaultAzureCredential() as creds, \
                AzureAIAgent.create_client(credential=creds) as client:
            
            for file_path in PRODUCT_INFO_FILE_PATHS:
                if not file_path.exists():
                    print(f"Error: File not found: {file_path}")
                    print(f"Note: Make sure the 'assets/data' directory exists with the product info markdown files.")
                    return
            
            for file_path in PRODUCT_INFO_FILE_PATHS:
                file = await upload_file(client, file_path)
                file_ids.append(file.id)
            
            # Create a vector store with the uploaded files
            vector_store = await create_vector_store(client, file_ids)
            vector_store_id = vector_store.id
            
            # Set up the agent with file search capability
            agent, thread = await setup_agent_with_file_search(
                client, 
                ai_agent_settings, 
                [vector_store.id]
            )
            agent_id = agent.id
            thread_id = thread.id
            
            await run_queries(agent, thread.id, queries_to_run)
            
            await cleanup_resources(
                client, 
                thread_id, 
                agent_id, 
                vector_store_id, 
                file_ids
            )
    except Exception as e:
        print(f"\nAn error occurred during execution: {str(e)}")
        
        try:
            if 'client' in locals():
                await cleanup_resources(
                    client, 
                    thread_id, 
                    agent_id, 
                    vector_store_id, 
                    file_ids
                )
        except Exception as cleanup_error:
            print(f"Error during resource cleanup: {str(cleanup_error)}")
        
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
