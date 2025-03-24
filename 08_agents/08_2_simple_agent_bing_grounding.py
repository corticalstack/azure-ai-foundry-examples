"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the Bing grounding tool from
    the Azure Agents service. Bing grounding enhances AI agents by connecting them to the Bing search engine,
    allowing them to retrieve up-to-date information from the web. This capability helps agents provide
    more accurate, current, and factual responses by grounding their knowledge in real-world data.
    
    This sample includes retry logic with exponential backoff to handle rate limiting issues.
    If you consistently get retry failures, double-check the Tokens Per Minute (TPM) 
    limit set against your AI Foundry model deployment.

USAGE:
    Set these environment variables with your own values:
    
    - AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING: The connection string for your Azure AI Foundry project.
      This can be obtained from the Azure AI Foundry portal under your project settings.
    
    - BING_CONNECTION_NAME: The name of your Bing connection in Azure AI Foundry. This connection must be 
      created in your Azure AI Foundry project.

# Note: Grounding with Bing Search only works with the following Azure OpenAI models:
# - gpt-3.5-turbo-0125
# - gpt-4-0125-preview
# - gpt-4-turbo-2024-04-09
# - gpt-4o
# For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/bing-grounding?tabs=python&pivots=overview

"""

import os
import pathlib
import time
import re
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageRole, BingGroundingTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configuration variables
# Using a compatible model for Bing grounding
MODEL_NAME = "gpt-4o"  # One of the supported models for Bing grounding
AGENT_NAME = "my-assistant"
AGENT_INSTRUCTIONS = "You are a helpful assistant"
SAMPLE_QUERY = "How does wikipedia explain 33 Thomas Street, Manhattan?"


def load_environment():
    """Load environment variables from .env file in current or parent directory"""
    current_dir = pathlib.Path(__file__).parent.absolute()
    root_dir = current_dir.parent
    load_dotenv(dotenv_path=root_dir / ".env")


def setup_client():
    """Create and return the AI Project client with proper authentication"""
    try:
        return AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=os.environ["AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING"],
        )
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise
    except Exception as e:
        print(f"Error setting up client: {e}")
        raise


def create_agent_with_bing_tool(client):
    """Create an agent with Bing grounding tool enabled
    
    This function configures the agent with the Bing connection and returns
    the created agent object.
    """
    try:
        # Get the Bing connection from the project
        bing_connection = client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
        conn_id = bing_connection.id
        print(conn_id)

        # Initialize agent bing tool and add the connection id
        # This enables the agent to search the web for information
        bing = BingGroundingTool(connection_id=conn_id)

        # Create agent with the bing tool
        agent = client.agents.create_agent(
            model=MODEL_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=bing.definitions,
            headers={"x-ms-enable-preview": "true"},
        )
        
        print(f"Created agent, ID: {agent.id}")
        return agent
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise
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


def run_conversation(client, agent_id, query):
    """Run a conversation with the agent using the provided query
    
    This function creates a thread, adds a message, processes the run with retry logic,
    and returns the response message.
    """
    try:
        thread = client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        message = client.agents.create_message(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=query,
        )
        print(f"Created message, ID: {message.id}")

        run = process_thread_run(client, thread_id=thread.id, agent_id=agent_id)
        
        if run is None:
            print("Failed to process the agent run after multiple retries")
            return thread.id, None
        elif run.status != "completed":
            print(f"Run finished with status: {run.status}")
            if hasattr(run, "last_error"):
                print(f"Run failed: {run.last_error}")
            return thread.id, None
            
        response_message = client.agents.list_messages(thread_id=thread.id).get_last_message_by_role(
            MessageRole.AGENT
        )
        
        return thread.id, response_message
    except Exception as e:
        print(f"Error in conversation: {e}")
        raise


def display_response(response_message):
    """Display the agent's response with any citations"""
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
    else:
        print("No response received from the agent.")


def main():
    """Main orchestration function"""
    load_environment()
    
    project_client = setup_client()
    
    try:
        with project_client:
            # Create agent with Bing tool
            agent = create_agent_with_bing_tool(project_client)
            agent_id = agent.id
            
            try:
                thread_id, response = run_conversation(project_client, agent_id, SAMPLE_QUERY)
                
                display_response(response)
            finally:
                # Cleanup: Delete the agent when done - must be inside the 'with' block otherwise you'll get a HTTP transport closed error.
                try:
                    project_client.agents.delete_agent(agent_id)
                    print("Deleted agent")
                except Exception as e:
                    print(f"Error deleting agent: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
