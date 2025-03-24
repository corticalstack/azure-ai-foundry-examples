"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service.

    The code interpreter tool allows AI agents to execute Python code, for example to analyze data,
    generate visualizations, and perform complex calculations.

    Be aware, if you consistently get retry failures, double-check the Tokens Per Minute (TPM) 
    limit set against your AI Foundry model deployment.

USAGE:
    Set these environment variables with your own values:
    
    - AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING: The connection string for your Azure AI Foundry project.
      This can be obtained from the Azure AI Foundry portal under your project settings.

# Note: Code interpreter works with the following Azure OpenAI models:
# - gpt-3.5-turbo
# - gpt-4
# - gpt-4-turbo
# - gpt-4o
# For more information, see: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/code-interpreter

"""

import os
import time
import re
import pathlib
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configuration variables
MODEL_NAME = "gpt-4o"
AGENT_NAME = "my-assistant"
AGENT_INSTRUCTIONS = "You are helpful assistant"
DATA_FILE_PATH = pathlib.Path(__file__).parent.parent / "assets" / "data" / "stockdata.csv"
USER_QUERY = """Plot a line chart showing the stock prices for 2013 for MSFT, IBM, SBUX, AAPL, and GSPC from the uploaded csv file.
        Normalize all stock prices to show percentage change relative to their initial value so they can be directly compared on the same scale.
        Save the plot as a file for me"""


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
    """Upload a file for use with the code interpreter
    
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


def create_agent_with_code_interpreter(client, file_ids):
    """Create an agent with code interpreter tool enabled
    
    Args:
        client: The AI Project client
        file_ids: List of file IDs to make available to the code interpreter
        
    Returns:
        The created agent object
        
    Raises:
        Exception: If agent creation fails
    """
    try:
        # Initialize code interpreter tool with the uploaded files
        # This enables the agent to analyze and process the data files
        code_interpreter = CodeInterpreterTool(file_ids=file_ids)

        # Create agent with the code interpreter tool
        agent = client.agents.create_agent(
            model=MODEL_NAME,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
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
        # Create user message in the thread
        message = client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=query,
        )
        print(f"Created message, message ID: {message.id}")

        # Process the thread with the agent
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


def save_generated_files(client, thread_id, script_dir):
    """Save any files generated by the code interpreter
    
    Args:
        client: The AI Project client
        thread_id: ID of the conversation thread
        script_dir: Directory to save files to
        
    Returns:
        List of saved file paths
    """
    try:
        messages = client.agents.list_messages(thread_id=thread_id)
        saved_files = []
        
        # Save any files generated by the code interpreter
        for file_path_annotation in messages.file_path_annotations:
            file_id = file_path_annotation.file_path.file_id
            file_name = f"{file_id}_annotation_file.png"
            file_path = script_dir / file_name
            client.agents.save_file(file_id=file_id, file_name=str(file_path))
            print(f"Saved annotation file to: {file_path}")
            saved_files.append(file_path)
            
        # Display the agent's last text message
        last_msg = messages.get_last_text_message_by_role(MessageRole.AGENT)
        if last_msg:
            print(f"Last Message: {last_msg.text.value}")
            
        return saved_files
    except Exception as e:
        print(f"Error saving generated files: {e}")
        return []


def main():
    """Main orchestration function"""
    load_environment()
    
    # Get the directory where this python script is located
    # This is where output files will be saved
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    project_client = setup_client()
    
    try:
        with project_client:
            # Upload data file for analysis
            file = upload_file(project_client, DATA_FILE_PATH)
            file_id = file.id
            
            try:
                # Create agent with code interpreter tool
                agent = create_agent_with_code_interpreter(project_client, [file_id])
                agent_id = agent.id
                
                try:
                    # Create thread for the conversation
                    thread = project_client.agents.create_thread()
                    thread_id = thread.id
                    print(f"Created thread, thread ID: {thread_id}")
                    
                    # Run the conversation with the user query
                    run = run_conversation(project_client, agent_id, thread_id, USER_QUERY)
                    
                    if run and run.status == "completed":
                        # Save any files generated by the code interpreter
                        save_generated_files(project_client, thread_id, script_dir)
                finally:
                    # Clean up the agent
                    project_client.agents.delete_agent(agent_id)
                    print("Deleted agent")
            finally:
                # Clean up the uploaded file
                project_client.agents.delete_file(file_id)
                print("Deleted file")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
