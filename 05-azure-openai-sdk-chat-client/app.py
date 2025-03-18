import sys
import os
import logging
from dotenv import load_dotenv
import pathlib

from openai import AzureOpenAI
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
logger = logging.getLogger("azure_openai_chat")


def get_endpoint_and_key():
    """
    Retrieve and validate the Azure OpenAI endpoint and API key from environment variables.

    Returns:
        tuple: (endpoint, api_key) or (None, None) if validation fails
    """
    # Get endpoint and API key from environment variables
    endpoint = os.getenv("AZURE_INFERENCE_ENDPOINT")
    api_key = os.getenv("AZURE_INFERENCE_API_KEY")

    # Check if the endpoint and API key are available
    if not endpoint:
        logger.error("Endpoint not found in environment variables")
        print("Please set AZURE_INFERENCE_ENDPOINT in your .env file")
        return None, None

    if not api_key:
        logger.error("API key not found in environment variables")
        print("Please set AZURE_INFERENCE_API_KEY in your .env file")
        return None, None

    # Check if the endpoint and API key have been updated
    if "<" in endpoint or "<" in api_key:
        logger.error("You need to update the endpoint or API key in the .env file")
        print("Please replace the placeholders with your actual endpoint and API key")
        return None, None

    return endpoint, api_key


def run_chat_loop(chat_client):
    """
    Run the interactive chat loop with the provided Azure OpenAI chat client.
    Maintains conversation history for context.

    Args:
        chat_client: The Azure OpenAI client
    """
    # Initialize conversation history with system message
    system_message = "You are a helpful AI assistant that answers questions."
    conversation_history = [{"role": "system", "content": system_message}]

    logger.info("Starting chat conversation loop")
    print("\n===== Azure OpenAI Chat Client =====")
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
            # Send the request to the model using the OpenAI client
            logger.info("Sending request to model")
            response = chat_client.chat.completions.create(
                model=chat_client.deployment_name, 
                messages=conversation_history,
                max_tokens=4096,
                temperature=0.7,
                top_p=1,
                stop=None
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
            
            # Print usage information if available
            if hasattr(response, 'usage') and response.usage:
                print("\nUsage:")
                print(f"  Prompt tokens: {response.usage.prompt_tokens}")
                print(f"  Completion tokens: {response.usage.completion_tokens}")
                print(f"  Total tokens: {response.usage.total_tokens}")
                
            print("\n" + "-" * 50 + "\n")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            print(f"Error generating response: {e}")


def initialize_client(endpoint, api_key):
    """
    Initialize the Azure OpenAI client.

    Args:
        endpoint: The validated endpoint URL
        api_key: The validated API key

    Returns:
        The Azure OpenAI client or None if initialization fails
    """
    try:
        logger.info("Creating Azure OpenAI client...")
        print("Creating Azure OpenAI client...")

        # Extract deployment name from the endpoint URL
        # Example endpoint: https://<resource-name>.openai.azure.com/openai/deployments/<deployment-name>/
        import re
        from urllib.parse import urlparse

        # Extract the deployment name
        deployment_match = re.search(r'/deployments/([^/]+)', endpoint)
        if not deployment_match:
            error_msg = "Deployment name not found in endpoint URL. The endpoint URL should include '/deployments/<deployment-name>/'."
            logger.error(error_msg)
            print(error_msg)
            raise ValueError(error_msg)
            
        deployment_name = deployment_match.group(1)
        
        # Extract the base endpoint (just the scheme and netloc)
        parsed_url = urlparse(endpoint)
        base_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        
        logger.info(f"Extracted base endpoint: {base_endpoint}")
        print(f"Extracted base endpoint: {base_endpoint}")

        # Create the Azure OpenAI client
        chat_client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-10-21",
            azure_endpoint=base_endpoint
        )

        # Store the deployment name as an attribute of the client for later use
        chat_client.deployment_name = deployment_name

        logger.info(f"Connected successfully! Using deployment: {deployment_name}")
        print(f"Connected successfully to Azure OpenAI client! Using deployment: {deployment_name}")
        return chat_client

    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}", exc_info=True)
        print(f"An unexpected error occurred: {ex}")

    return None


def main():
    """Main entry point for the application."""
    logger.info("=== Azure OpenAI Chat Client ===")
    logger.info("See README.md for setup instructions")

    print("Initializing client...")

    # Get and validate endpoint and API key
    endpoint, api_key = get_endpoint_and_key()
    if not endpoint or not api_key:
        return

    # Initialize the client
    chat_client = initialize_client(endpoint, api_key)
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
