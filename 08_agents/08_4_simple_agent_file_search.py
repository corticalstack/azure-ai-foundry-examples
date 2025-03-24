"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with file searching from the Azure Agents service.

    Searches through multiple uploaded documents to find relevant information and answer questions based on the content. 

    Be aware, if you consistently get retry failures, double-check the Tokens Per Minute (TPM) 
    limit set against your AI Foundry model deployment.

USAGE:
    Set these environment variables with your own values:
    
    - AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING: The connection string for your Azure AI Foundry project.
      This can be obtained from the Azure AI Foundry portal under your project settings.
      
    Command-line arguments:
    
    - --query N: Run a specific test query (N is a number from 1 to 4)
    - --custom-query "Your query here": Run a custom query instead of the predefined test queries
    - --list-queries: List all available test queries and exit
    
    Examples:
    
    python 13_4_simple_agent_file_search.py                                  # Run all test queries
    python 13_4_simple_agent_file_search.py --query 2                        # Run only the second test query
    python 13_4_simple_agent_file_search.py --list-queries                   # List all available test queries
    python 13_4_simple_agent_file_search.py --custom-query "Tell me about SmartView Glasses warranty"  # Run a custom query

# Note: File search works with the following Azure OpenAI models:
# - gpt-3.5-turbo
# - gpt-4
# - gpt-4-turbo
# - gpt-4o
# For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/file-search

"""

import os
import time
import re
import pathlib
import argparse
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, FilePurpose, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configuration variables
MODEL_NAME = "gpt-4o"
AGENT_NAME = "my-assistant"
AGENT_INSTRUCTIONS = """You are a helpful assistant that can search information from uploaded files. 
You have access to multiple product information files from Contoso. 
When asked about Contoso products, provide comprehensive information and compare products when appropriate, citing the specific files you're retrieving information from."""

# List of product info files to upload
PRODUCT_INFO_FILE_PATHS = [
    pathlib.Path(__file__).parent.parent / "assets/data/product_info_1.md",
    pathlib.Path(__file__).parent.parent / "assets/data/product_info_2.md",
]

# Sample test queries for different search scenarios (find context in one file or multiple files)
TEST_QUERIES = [
    "Tell me about all Contoso products you know about and compare their features, warranty, and return policies.",
    "What are the features of the SmartView Glasses?",
    "Tell me about the SmartHub Control Center.",
    "Compare the warranty periods of all Contoso products."
]


def load_environment():
    """Load environment variables from .env file in current or parent directory"""
    current_dir = pathlib.Path(__file__).parent.absolute()
    root_dir = current_dir.parent
    load_dotenv(dotenv_path=root_dir / ".env")


def setup_client():
    """Create and return the AI Project client with proper authentication
    
    Returns:
        AIProjectClient: Authenticated client for interacting with Azure AI Foundry
    
    Raises:
        KeyError: If required environment variables are missing
        Exception: For other client setup errors
    """
    try:
        return AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING"]
        )
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise
    except Exception as e:
        print(f"Error setting up client: {e}")
        raise


def upload_file(client, file_path):
    """Upload a file for use with the file search tool
    
    Args:
        client: The AI Project client
        file_path: Path to the file to upload
        
    Returns:
        The uploaded file object
        
    Raises:
        Exception: If file upload fails
    """
    try:
        file = client.agents.upload_file_and_poll(
            file_path=file_path, purpose=FilePurpose.AGENTS
        )
        print(f"Uploaded file, file ID: {file.id}")
        return file
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise


def create_vector_store(client, file_ids):
    """Create a vector store from the uploaded files
    
    Args:
        client: The AI Project client
        file_ids: List of file IDs to include in the vector store
        
    Returns:
        The created vector store object
        
    Raises:
        Exception: If vector store creation fails
    """
    try:
        vector_store = client.agents.create_vector_store_and_poll(
            file_ids=file_ids, 
            name="my_vectorstore"
        )
        print(f"Created vector store, vector store ID: {vector_store.id}")
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        raise


def create_agent_with_file_search(client, vector_store_ids):
    """Create an agent with file search tool enabled
    
    Args:
        client: The AI Project client
        vector_store_ids: List of vector store IDs to make available to the file search tool
        
    Returns:
        The created agent object
        
    Raises:
        Exception: If agent creation fails
    """
    try:
        # Initialize file search tool with the vector stores
        file_search = FileSearchTool(vector_store_ids=vector_store_ids)

        # Create agent with the file search tool
        agent = client.agents.create_agent(
            model=MODEL_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )
        
        print(f"Created agent, agent ID: {agent.id}")
        return agent
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise


def process_thread_run(client, thread_id, agent_id, max_retries=3, initial_retry_delay=1):
    """Ask the agent to process the thread and generate a response
    
    This function handles rate limiting with exponential backoff and retries.
    
    Args:
        client: The AI Project client
        thread_id: ID of the conversation thread
        agent_id: ID of the agent
        max_retries: Maximum number of retry attempts (default 3)
        initial_retry_delay: Initial delay in seconds between retries (will increase exponentially)
        
    Returns:
        Run object if successful, None if error occurs
    """
    retry_count = 0
    retry_delay = initial_retry_delay
    
    while retry_count <= max_retries:
        try:
            run = client.agents.create_run(
                thread_id=thread_id,
                agent_id=agent_id
            )

            # Poll the run status until completion or error
            # Status can be: queued, in_progress, requires_action, completed, failed
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = client.agents.get_run(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            # If the run failed due to rate limiting, extract the wait time and retry
            if run.status == "failed" and hasattr(run, "last_error") and run.last_error.get("code") == "rate_limit_exceeded":
                error_message = run.last_error.get("message", "")
                wait_seconds = 0

                # Try to extract the suggested wait time from the error message
                time_match = re.search(r'Try again in (\d+) seconds', error_message)
                if time_match:
                    wait_seconds = int(time_match.group(1))
                else:
                    # If unable to extract suggested wait time, use exponential backoff
                    wait_seconds = retry_delay
                    retry_delay *= 2  # Exponential backoff
                
                retry_count += 1
                if retry_count <= max_retries:
                    print(f"⏳ Rate limit exceeded. Waiting for {wait_seconds} seconds before retry ({retry_count}/{max_retries})...")
                    time.sleep(wait_seconds)
                    continue
                else:
                    print(f"❌ Rate limit exceeded. Maximum retries ({max_retries}) reached.")
                    return None
            
            # If we got here and status is not "completed", something else went wrong
            if run.status != "completed":
                print(f"🤖 Run completed with status: {run.status}")
                print(f"Error details: {run.last_error if hasattr(run, 'last_error') else 'Unknown error'}")
                return None
                
            print(f"🤖 Run completed successfully with status: {run.status}")
            return run
            
        except Exception as e:
            print(f"❌ Error processing thread run: {str(e)}")
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Maximum retries ({max_retries}) reached.")
                return None
    
    return None


def run_conversation(client, agent_id, thread_id, query):
    """Run a conversation with the agent using the provided query
    
    Args:
        client: The AI Project client
        agent_id: ID of the agent
        thread_id: ID of the conversation thread
        query: The user's query to process
        
    Returns:
        The run object if successful, None otherwise
    """
    try:
        message = client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=query,
        )
        print(f"Created message, message ID: {message.id}")

        run = process_thread_run(client, thread_id=thread_id, agent_id=agent_id)
        
        if run is None:
            print("Failed to process the agent run after multiple retries")
        elif run.status != "completed":
            print(f"Run finished with status: {run.status}")
            if hasattr(run, "last_error"):
                print(f"Run failed: {run.last_error}")
                
        return run
    except Exception as e:
        print(f"Error in conversation: {e}")
        return None


def display_messages(client, thread_id, limit=2):
    """Display messages in the thread
    
    Args:
        client: The AI Project client
        thread_id: ID of the conversation thread
        limit: Number of most recent messages to display (default: 2, which shows the last query and response)
               If None, displays all messages in the thread
    """
    messages = client.agents.list_messages(thread_id=thread_id)
    messages_list = messages.data
    
    # Get messages based on limit
    if limit is not None:
        recent_messages = messages_list[:limit]
    else:
        recent_messages = messages_list
        
    recent_messages.reverse()  # Reverse to show in chronological order
    
    print(f"\n\033[36m{'='*40} CONVERSATION {'='*40}\033[0m")
    
    for message in recent_messages:
        role = message.role  
        if role == "user":
            print(f"\n\033[33mUser Query:\033[0m")
        else:
            print(f"\n\033[32mAssistant Response:\033[0m")
        
        for content_item in message.content:
            if content_item.type == 'text':
                print(content_item.text.value)               
                annotations = content_item.text.annotations
                if annotations:
                    print("\n\033[36mFile Citations:\033[0m")
                    for annotation in annotations:
                        if annotation.type == 'file_citation':
                            file_citation = annotation.file_citation
                            file_id = file_citation.file_id
                            file_info = client.agents.get_file(file_id=file_id)
                            print(f"- \033[36mFile:\033[0m {file_info.filename}")
    
    print(f"\n\033[36m{'='*90}\033[0m")


def upload_files(client, file_paths):
    """Upload multiple files for use with the file search tool
    
    Args:
        client: The AI Project client
        file_paths: List of paths to the files to upload
        
    Returns:
        List of uploaded file IDs
        
    Raises:
        Exception: If file upload fails
    """
    file_ids = []
    try:
        for file_path in file_paths:
            file = upload_file(client, file_path)
            file_ids.append(file.id)
        return file_ids
    except Exception as e:
        # Clean up any files that were uploaded before the error
        for file_id in file_ids:
            try:
                client.agents.delete_file(file_id)
                print(f"Cleaned up file ID: {file_id}")
            except Exception as cleanup_error:
                print(f"Error cleaning up file {file_id}: {cleanup_error}")
        raise


def parse_arguments():
    """Parse command-line arguments
    
    Returns:
        Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Run file search agent with multiple files")
    
    # Add query selection argument
    parser.add_argument(
        "--query", 
        type=int, 
        choices=range(1, len(TEST_QUERIES) + 1),
        help=f"Select a specific query to run (1-{len(TEST_QUERIES)}). If not provided, all queries will be run."
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


def main():
    """Main orchestration function"""
    args = parse_arguments()
    
    # List queries if requested
    if args.list_queries:
        print("\nAvailable test queries:")
        for i, query in enumerate(TEST_QUERIES):
            print(f"{i+1}. {query}")
        return
    
    queries_to_run = []
    if args.custom_query:
        queries_to_run = [args.custom_query]
        print(f"\nRunning custom query: {args.custom_query}")
    elif args.query:
        query_index = args.query - 1  # Convert to 0-based index
        queries_to_run = [TEST_QUERIES[query_index]]
        print(f"\nRunning test query {args.query}: {queries_to_run[0]}")
    else:
        queries_to_run = TEST_QUERIES
        print(f"\nRunning all {len(TEST_QUERIES)} test queries")
    
    # Load environment and set up client
    load_environment()
    project_client = setup_client()
    
    try:
        with project_client:
            file_ids = upload_files(project_client, PRODUCT_INFO_FILE_PATHS)
            
            try:
                # Create vector store with all file IDs
                vector_store = create_vector_store(project_client, file_ids)
                vector_store_id = vector_store.id
                
                try:
                    # Create agent with file search tool
                    agent = create_agent_with_file_search(project_client, [vector_store_id])
                    agent_id = agent.id
                    
                    try:
                        for i, query in enumerate(queries_to_run):
                            print(f"\n\n{'='*80}\nRunning query {i+1}/{len(queries_to_run)}:\n{query}\n{'='*80}\n")
                            
                            # Create a new thread for each query
                            thread = project_client.agents.create_thread()
                            thread_id = thread.id
                            print(f"Created thread for query {i+1}, thread ID: {thread_id}")
                            
                            run = run_conversation(project_client, agent_id, thread_id, query)
                            
                            if run and run.status == "completed":
                                display_messages(project_client, thread_id, limit=None)
                            
                            # Add a short delay between queries to avoid rate limiting
                            if i < len(queries_to_run) - 1:
                                time.sleep(1)
                    finally:
                        project_client.agents.delete_agent(agent_id)
                        print("\nDeleted agent")
                finally:
                    project_client.agents.delete_vector_store(vector_store_id)
                    print("Deleted vector store")
            finally:
                for file_id in file_ids:
                    project_client.agents.delete_file(file_id)
                    print(f"Deleted file: {file_id}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
