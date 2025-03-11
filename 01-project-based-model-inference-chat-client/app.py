import sys
import re
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Tuple
import pathlib

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError

# Load environment variables from .env file
# Look for .env in the current directory and parent directory
current_dir = pathlib.Path(__file__).parent.absolute()
root_dir = current_dir.parent
load_dotenv(dotenv_path=root_dir / ".env")

# Configure logging - only to file, not to console to avoid polluting chat output
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)
# Get the directory name programmatically for the log file name
dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
log_file = f"{dir_name}.log"
logging.basicConfig(
    level=numeric_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file)],
)
logger = logging.getLogger("azure_ai_foundry_chat")


def get_project_connection_string() -> Optional[str]:
    """
    Retrieve and validate the Azure AI Foundry project connection string from environment variables.

    Returns:
        Optional[str]: The validated project connection string or None if validation fails
    """
    # Get connection string from environment variable
    conn_str = os.getenv("AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING")

    # Check if the connection string is available
    if not conn_str:
        logger.error("Project connection string not found in environment variables")
        print(
            "Please create a .env file based on .env.example and set your project connection string"
        )
        return None

    # Check if the connection string has been updated
    if "<" in conn_str:
        logger.error(
            "You need to update the project connection string in the .env file"
        )
        print(
            "Please replace the placeholder with your actual project connection string"
        )
        return None

    # Validate connection string format
    pattern = r"^[^;]+\.api\.azureml\.ms;[^;]+;[^;]+;[^;]+$"
    if not re.match(pattern, conn_str):
        logger.error(
            "The connection string should follow the format: <region>.api.azureml.ms;<project_id>;<hub_name>;<project_name>"
        )
        print(
            "The connection string should follow the format: <region>.api.azureml.ms;<project_id>;<hub_name>;<project_name>"
        )
        return None

    return conn_str


def run_chat_loop(chat_client):
    """
    Run the interactive chat loop with the provided Azure AI Founbdry AI Servces model inference chat client.
    Maintains conversation history for context.

    Args:
        chat_client: The Azure AI Foundry (AI Services AI model inference) chat completions client
    """
    # Initialize conversation history with system message
    system_message = "You are a helpful AI assistant that answers questions."
    conversation_history = [{"role": "system", "content": system_message}]

    logger.info("Starting chat conversation loop")
    print("\n===== Azure AI Model Inference Chat Client =====")
    print(
        "Starting a new conversation. Type 'quit' to quit or 'clear' to reset conversation history.\n"
    )

    # Chat loop
    while True:
        # Get a chat completion based on a user-provided prompt
        user_prompt = input("Enter a question (or 'quit' to quit, 'clear' to reset): ")

        if user_prompt.lower() in ["quit", "q"]:
            logger.info("User requested to exit")
            print("Goodbye!")
            break

        if user_prompt.lower() in ["clear"]:
            logger.info("User requested to clear conversation history")
            conversation_history = [{"role": "system", "content": system_message}]
            print("Conversation history cleared. Starting fresh.")
            continue

        if not user_prompt.strip():
            logger.warning("Empty prompt received")
            print("Please enter a valid question.")
            continue

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_prompt})

        logger.debug(f"User prompt: {user_prompt}")
        logger.debug(f"Conversation history length: {len(conversation_history)}")
        print("Generating response...")

        try:
            # Send the complete conversation history for context
            logger.info("Sending request to model")
            response = chat_client.complete(
                model="gpt-4o-mini",  # IMPORTANT! Change model deployment name here as appripriate
                messages=conversation_history,
            )

            # Get the assistant's response
            assistant_response = response.choices[0].message.content

            # Add assistant response to history
            conversation_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            logger.debug(f"Response received: {assistant_response[:50]}...")
            print("\nResponse:")
            print(assistant_response)
            print("\n" + "-" * 50 + "\n")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            print(f"Error generating response: {e}")


def initialize_client(connection_string):
    """
    Initialize the Azure AI Foundry client.

    Args:
        connection_string: The validated connection string

    Returns:
        The chat completions client or None if initialization fails
    """
    try:
        logger.info("Connecting to Azure AI Foundry...")
        print("Connecting to Azure AI Foundry...")

        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=connection_string,
        )

        # Get a chat client
        logger.info("Creating AI Foundry AI Model inference completion client...")
        chat_client = project_client.inference.get_chat_completions_client()

        logger.info("Connected successfully!")
        print(
            "Connected successfully to Azure AI model inference service completion client!"
        )
        return chat_client

    except ClientAuthenticationError as auth_error:
        logger.error(f"Authentication error: {auth_error}")
        print(f"Authentication error: {auth_error}")
    except ServiceRequestError as req_error:
        logger.error(f"Service request error: {req_error}")
        print(f"Service request error: {req_error}")
    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}", exc_info=True)
        print(f"An unexpected error occurred: {ex}", exc_info=True)

    return None


def main():
    """Main entry point for the application."""
    logger.info("=== Azure AI Foundry AI Model Inference Chat Client ===")
    logger.info("See README.md for setup instructions")

    print("Initializing client...")

    # Get and validate connection string
    connection_string = get_project_connection_string()
    if not connection_string:
        return

    # Initialize the client
    chat_client = initialize_client(connection_string)
    if not chat_client:
        return

    # Run the chat loop
    try:
        run_chat_loop(chat_client)
    except Exception as ex:
        logger.error(f"An error occurred during chat: {ex}", exc_info=True)
        print(f"Error: An error occurred during chat")
        print(f"Details: {ex}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
