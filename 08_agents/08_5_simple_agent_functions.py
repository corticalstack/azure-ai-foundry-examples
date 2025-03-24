# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with developer-defined custom functions from the Azure Agents service.

    Be aware, if you consistently get retry failures, double-check the Tokens Per Minute (TPM) 
    limit set against your AI Foundry model deployment.

USAGE:
    Set these environment variables with your own values:
    
    - AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING: The connection string for your Azure AI Foundry project.
      This can be obtained from the Azure AI Foundry portal under your project settings.
      
    Command-line arguments:
    
    - --query N: Run a specific test query (N is a number from 1 to 3)
    - --custom-query "Your query here": Run a custom query instead of the predefined test queries
    - --list-queries: List all available test queries and exit
    
    Examples:
    
    python 13_5_simple_agent_functions.py                                  # Run all test queries
    python 13_5_simple_agent_functions.py --query 2                        # Run only the second test query
    python 13_5_simple_agent_functions.py --list-queries                   # List all available test queries
    python 13_5_simple_agent_functions.py --custom-query "What's the weather in New York?"  # Run a custom query

# Note: Function tools work with the following Azure OpenAI models:
# - gpt-3.5-turbo
# - gpt-4
# - gpt-4-turbo
# - gpt-4o
# For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/function-calling
"""

import os
import time
import re
import pathlib
import argparse
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FunctionTool, 
    RequiredFunctionToolCall, 
    SubmitToolOutputsAction, 
    ToolOutput,
    MessageRole
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from example_user_functions import user_functions  # Import our test collection of custom defined functions

MODEL_NAME = "gpt-4o"
AGENT_NAME = "my-assistant"
AGENT_INSTRUCTIONS = "You are a helpful assistant"

# Sample test queries for different function calling scenarios
TEST_QUERIES = [
    "Convert 25 degrees Celsius to Fahrenheit.",
    "What's the weather for Geneva?",
    "Compose an email with the datetime and weather information for Geneva.",
    "What is the sum of 45 and 55?",
    "Retrieve user information for user ID 1."
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


def create_agent_with_functions(client, functions_tool):
    """Create an agent with function tool enabled
    
    Args:
        client: The AI Project client
        functions_tool: The function tool with user-defined functions
        
    Returns:
        The created agent object
        
    Raises:
        Exception: If agent creation fails
    """
    try:
        agent = client.agents.create_agent(
            model=MODEL_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=functions_tool.definitions,
        )
        
        print(f"Created agent, agent ID: {agent.id}")
        return agent
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise


def process_function_calls(client, thread_id, run_id, functions_tool, max_retries=3, initial_retry_delay=1):
    """Process function calls from the agent and handle retries for rate limiting
    
    Args:
        client: The AI Project client
        thread_id: ID of the conversation thread
        run_id: ID of the run
        functions_tool: The function tool with user-defined functions
        max_retries: Maximum number of retry attempts (default 3)
        initial_retry_delay: Initial delay in seconds between retries (will increase exponentially)
        
    Returns:
        Run object if successful, None if error occurs
    """
    retry_count = 0
    retry_delay = initial_retry_delay
    run = None
    
    while retry_count <= max_retries:
        try:
            run = client.agents.get_run(thread_id=thread_id, run_id=run_id)
            
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = client.agents.get_run(thread_id=thread_id, run_id=run_id)
                
                # Handle function calls if required
                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        client.agents.cancel_run(thread_id=thread_id, run_id=run_id)
                        return None

                    tool_outputs = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredFunctionToolCall):
                            try:
                                print(f"Executing tool call: {tool_call}")
                                output = functions_tool.execute(tool_call)
                                tool_outputs.append(
                                    ToolOutput(
                                        tool_call_id=tool_call.id,
                                        output=output,
                                    )
                                )
                            except Exception as e:
                                print(f"Error executing tool_call {tool_call.id}: {e}")

                    print(f"Tool outputs: {tool_outputs}")
                    if tool_outputs:
                        client.agents.submit_tool_outputs_to_run(
                            thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs
                        )
                
                # Handle rate limiting
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
                        # Create a new run after rate limit error
                        run = client.agents.create_run(thread_id=thread_id, agent_id=agent_id)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded. Maximum retries ({max_retries}) reached.")
                        return None
            
            # If we got here and status is not "completed", something else went wrong
            if run.status != "completed":
                print(f"🤖 Run completed with status: {run.status}")
                print(f"Error details: {run.last_error if hasattr(run, 'last_error') else 'Unknown error'}")
                
            print(f"🤖 Run completed with status: {run.status}")
            return run
            
        except Exception as e:
            print(f"❌ Error processing run: {str(e)}")
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Maximum retries ({max_retries}) reached.")
                return None
    
    return run


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
        # Create user message in the thread
        message = client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=query,
        )
        print(f"Created message, message ID: {message.id}")

        # Create a run for the agent to process the message
        run = client.agents.create_run(
            thread_id=thread_id,
            agent_id=agent_id
        )
        print(f"Created run, run ID: {run.id}")
        
        # Process the run with function calls
        run = process_function_calls(client, thread_id, run.id, functions)
        
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


def display_messages(client, thread_id):
    """Display all messages in the thread
    
    Args:
        client: The AI Project client
        thread_id: ID of the conversation thread
    """
    try:
        messages = client.agents.list_messages(thread_id=thread_id)

        print("\n--- Conversation ---")
        for text_message in messages.text_messages:
            if hasattr(text_message, 'role'):
                role = "User" if text_message.role == MessageRole.USER else "Assistant"
                print(f"{role}: {text_message.text.value}")
            else:
                print(f"Assistant: {text_message.text['value']}")
        print("-------------------\n")
    except Exception as e:
        print(f"Error displaying messages: {e}")


def parse_arguments():
    """Parse command-line arguments
    
    Returns:
        Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Run function agent with custom functions")
    
    parser.add_argument(
        "--query", 
        type=int, 
        choices=range(1, len(TEST_QUERIES) + 1),
        help=f"Select a specific query to run (1-{len(TEST_QUERIES)}). If not provided, all queries will be run."
    )
    
    parser.add_argument(
        "--custom-query", 
        type=str,
        help="Run a custom query instead of the predefined test queries"
    )
    
    parser.add_argument(
        "--list-queries", 
        action="store_true",
        help="List all available test queries and exit"
    )
    
    return parser.parse_args()


def main():
    """Main orchestration function"""
    args = parse_arguments()
    
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
    
    load_environment()
    project_client = setup_client()
    
    try:
        with project_client:
            # Initialize function tool with user functions
            global functions
            functions = FunctionTool(functions=user_functions)
            
            try:
                # Create agent with function tool
                agent = create_agent_with_functions(project_client, functions)
                global agent_id
                agent_id = agent.id
                
                try:
                    # Run each query with its own thread
                    for i, query in enumerate(queries_to_run):
                        print(f"\n\n{'='*80}\nRunning query {i+1}/{len(queries_to_run)}:\n{query}\n{'='*80}\n")
                        
                        # Create a new thread for each query
                        thread = project_client.agents.create_thread()
                        thread_id = thread.id
                        print(f"Created thread for query {i+1}, thread ID: {thread_id}")
                        
                        run = run_conversation(project_client, agent_id, thread_id, query)
                        
                        if run and run.status == "completed":
                            display_messages(project_client, thread_id)
                        
                        # Add a short delay between queries to avoid rate limiting
                        if i < len(queries_to_run) - 1:
                            time.sleep(1)
                finally:
                    # Clean up the agent
                    project_client.agents.delete_agent(agent_id)
                    print("\nDeleted agent")
            except Exception as e:
                print(f"Error in agent operations: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
