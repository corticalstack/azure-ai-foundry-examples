import os
import sys
import logging
from dotenv import load_dotenv
import pathlib

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.prompts import PromptTemplate
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError

# Load environment variables from .env file
# Look for .env in the current directory and parent directory
current_dir = pathlib.Path(__file__).parent.absolute()
root_dir = current_dir.parent
load_dotenv(dotenv_path=root_dir / ".env")

# Configure logging - only to file, not to console to avoid polluting output
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
logger = logging.getLogger("azure_ai_inference_prompt_template")


def get_endpoint_and_key():
    """
    Retrieve and validate the Azure AI Inference endpoint and API key from environment variables.

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


def initialize_client(endpoint, api_key):
    """
    Initialize the Azure AI Inference chat client.

    Args:
        endpoint: The validated endpoint URL
        api_key: The validated API key

    Returns:
        The chat completions client or None if initialization fails
    """
    try:
        logger.info("Creating Azure AI Inference chat client...")
        print("Creating Azure AI Inference chat client...")

        chat_client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )

        logger.info("Connected successfully!")
        print("Connected successfully to Azure AI Inference chat client!")
        return chat_client

    except ClientAuthenticationError as auth_error:
        logger.error(f"Authentication error: {auth_error}")
        print(f"Authentication error: {auth_error}")
    except ServiceRequestError as req_error:
        logger.error(f"Service request error: {req_error}")
        print(f"Service request error: {req_error}")
    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}", exc_info=True)
        print(f"An unexpected error occurred: {ex}")

    return None


def run_prompt_template_example(chat_client):
    """
    Run a simple example using PromptTemplate to create a prompt and get a completion.

    Args:
        chat_client: The Azure AI Inference chat completions client
    """
    logger.info("Running prompt template example")
    print("\n===== Azure AI Inference Prompt Template Example =====")
    
    try:
        # Create a prompt template from an inline string (using mustache syntax)
        prompt_template = PromptTemplate.from_string(prompt_template="""
system:
You are a helpful writing assistant.
The user's first name is {{first_name}} and their last name is {{last_name}}.

user:
Write me a poem about flowers
""")

        # Generate messages from the template, passing in the context as variables
        print("\nCreating messages from template with variables:")
        messages = prompt_template.create_messages(first_name="Jane", last_name="Doe")
        print("Generated messages:")
        for message in messages:
            print(f"Role: {message['role']}")
            print(f"Content: {message['content']}")
            print("---")

        # Prepare the payload with the messages
        logger.info("Sending request to model")
        print("\nSending request to model...")
        payload = {
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 1,
            "stop": []
        }
        
        # Send the request to the model
        response = chat_client.complete(payload)

        # Get the assistant's response
        assistant_response = response.choices[0].message.content

        logger.debug(f"Response received: {assistant_response[:50]}...")
        print("\nResponse:")
        print(assistant_response)
        
        # Print usage information if available
        if hasattr(response, 'usage') and response.usage:
            print("\nUsage:")
            print(f"  Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  Completion tokens: {response.usage.completion_tokens}")
            print(f"  Total tokens: {response.usage.total_tokens}")

    except Exception as e:
        logger.error(f"Error in prompt template example: {e}")
        print(f"Error in prompt template example: {e}")


def main():
    """Main entry point for the application."""
    logger.info("=== Azure AI Inference Prompt Template Example ===")
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

    # Run the prompt template example
    try:
        run_prompt_template_example(chat_client)
    except Exception as ex:
        logger.error(f"An error occurred: {ex}", exc_info=True)
        print(f"Error: An error occurred")
        print(f"Details: {ex}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
