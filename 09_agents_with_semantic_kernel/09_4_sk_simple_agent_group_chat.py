"""
Agent Group Chat with Semantic Kernel

This example demonstrates how to create a collaborative agent group chat system using 
Semantic Kernel. The system consists of two specialized AI agents:

1. Reviewer Agent: Analyzes content and provides improvement suggestions
2. Writer Agent: Rewrites content based on the reviewer's suggestions

The agents work together in a turn-based conversation to iteratively improve content
provided by the user. The conversation continues until the reviewer determines the
content is satisfactory.

Usage:
    Run this script directly to start an interactive chat session:
      
    - Type your content when prompted
    - Or use '@filename' to load content from a file
    - Type 'reset' to restart the conversation
    - Type 'exit' to quit
"""

import asyncio
import os
from typing import Any, List, Optional, TypeVar

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.functions.kernel_function_metadata import KernelFunctionMetadata

# Type variable for generic function results
T = TypeVar('T')

# Constants
REVIEWER_NAME = "Reviewer"
WRITER_NAME = "Writer"
TERMINATION_KEYWORD = "yes"
HISTORY_TARGET_COUNT = 5
MAX_ITERATIONS = 10


def create_kernel() -> Kernel:
    """
    Creates and configures a Semantic Kernel instance with Azure OpenAI services.
    
    This function initializes a new Kernel and adds the Azure OpenAI ChatCompletion
    service to it. The service configuration is loaded from environment variables.
    
    Returns:
        Kernel: A configured Semantic Kernel instance ready for agent use
    """
    kernel = Kernel()
    kernel.add_service(service=AzureChatCompletion())
    return kernel


def create_agent(
    kernel: Kernel,
    name: str,git add 
    instructions: str
) -> ChatCompletionAgent:
    """
    Creates and configures a single AI agent with specific instructions.
    
    This function initializes a ChatCompletionAgent with the provided name and
    instructions, using the shared kernel instance.
    
    Args:
        kernel: The Semantic Kernel instance to use for the agent
        name: The name of the agent (e.g., "Reviewer", "Writer")
        instructions: The instructions that define the agent's behavior
        
    Returns:
        ChatCompletionAgent: A configured agent ready for use in the group chat
    """
    return ChatCompletionAgent(
        kernel=kernel,
        name=name,
        instructions=instructions,
    )


def create_agents(kernel: Kernel) -> List[ChatCompletionAgent]:
    """
    Creates and configures the specialized AI agents for the group chat.
    
    This function creates two agents with specific roles:
    1. Reviewer: Analyzes content and provides improvement suggestions
    2. Writer: Rewrites content based on the reviewer's suggestions
    
    Each agent has tailored instructions that define its behavior and responsibilities
    within the collaborative workflow.
    
    Args:
        kernel: The Semantic Kernel instance to use for the agents
        
    Returns:
        List[ChatCompletionAgent]: A list containing the configured reviewer and writer agents
    """
    # Define agent instructions
    reviewer_instructions = """
Your responsibility is to review and identify how to improve user provided content.
If the user has provided input or direction for content already provided, specify how to address this input.
Never directly perform the correction or provide an example.
Once the content has been updated in a subsequent response, review it again until it is satisfactory.

RULES:
- Only identify suggestions that are specific and actionable.
- Verify previous suggestions have been addressed.
- Never repeat previous suggestions.
"""

    writer_instructions = """
Your sole responsibility is to rewrite content according to review suggestions.
- Always apply all review directions.
- Always revise the content in its entirety without explanation.
- Never address the user.
"""
    
    # Create agents using the parameterized function
    agent_reviewer = create_agent(kernel, REVIEWER_NAME, reviewer_instructions)
    agent_writer = create_agent(kernel, WRITER_NAME, writer_instructions)
    
    return [agent_reviewer, agent_writer]


def create_selection_function(kernel: Kernel) -> KernelFunctionFromPrompt:
    """
    Creates a function that determines which agent should respond next in the conversation.
    
    This function defines the turn-taking logic between the reviewer and writer agents.
    It analyzes the most recent message to determine who should speak next, ensuring
    a collaborative workflow where:
    - Reviewer analyzes user input and writer output
    - Writer implements reviewer suggestions
    
    Args:
        kernel: The Semantic Kernel instance to use for the function
        
    Returns:
        KernelFunctionFromPrompt: A kernel function that selects the next agent
    """
    return KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""
Examine the provided RESPONSE and choose the next participant.
State only the name of the chosen participant without explanation.
Never choose the participant named in the RESPONSE.

Choose only from these participants:
- {REVIEWER_NAME}
- {WRITER_NAME}

Rules:
- If RESPONSE is user input, it is {REVIEWER_NAME}'s turn.
- If RESPONSE is by {REVIEWER_NAME}, it is {WRITER_NAME}'s turn.
- If RESPONSE is by {WRITER_NAME}, it is {REVIEWER_NAME}'s turn.

RESPONSE:
{{{{$lastmessage}}}}
""",
    )


def create_termination_function(kernel: Kernel) -> KernelFunctionFromPrompt:
    """
    Creates a function that determines when the conversation should end.
    
    This function checks if the content has been deemed satisfactory by the reviewer.
    When the reviewer no longer has suggestions for improvement, the conversation
    can terminate.
    
    Args:
        kernel: The Semantic Kernel instance to use for the function
        
    Returns:
        KernelFunctionFromPrompt: A kernel function that determines if the conversation should end
    """
    return KernelFunctionFromPrompt(
        function_name="termination",
        prompt=f"""
Examine the RESPONSE and determine whether the content has been deemed satisfactory.
If the content is satisfactory, respond with a single word without explanation: {TERMINATION_KEYWORD}.
If specific suggestions are being provided, it is not satisfactory.
If no correction is suggested, it is satisfactory.

RESPONSE:
{{{{$lastmessage}}}}
""",
    )


def create_agent_group_chat(
    kernel: Kernel, 
    agents: List[ChatCompletionAgent]
) -> AgentGroupChat:
    """
    Creates and configures the agent group chat with selection and termination strategies.
    
    This function sets up the collaborative environment where agents can work together,
    defining:
    - Which agents participate in the conversation
    - How to determine which agent speaks next
    - When the conversation should end
    - How to manage conversation history to optimize performance
    
    Args:
        kernel: The Semantic Kernel instance to use
        agents: List of agents to include in the group chat
        
    Returns:
        AgentGroupChat: A configured group chat ready for interaction
    """
    # Extract the reviewer and writer agents from the list
    agent_reviewer = next(agent for agent in agents if agent.name == REVIEWER_NAME)
    
    # Create functions for agent selection and conversation termination
    selection_function = create_selection_function(kernel)
    termination_function = create_termination_function(kernel)
    
    # Create a history reducer to optimize token usage by limiting context
    # This keeps only the most recent messages, reducing token consumption
    # while maintaining enough context for coherent conversation
    history_reducer = ChatHistoryTruncationReducer(target_count=HISTORY_TARGET_COUNT)
    
    # Define a parser function to extract agent names from selection function results
    def parse_selection_result(result: Any) -> str:
        """Parse the result from the selection function to get the next agent's name."""
        return str(result.value[0]).strip() if result.value[0] is not None else WRITER_NAME
    
    # Define a parser function to determine if the conversation should terminate
    def parse_termination_result(result: Any) -> bool:
        """Parse the result from the termination function to determine if conversation is complete."""
        return TERMINATION_KEYWORD in str(result.value[0]).lower()
    
    # Create the agent group chat with all components
    return AgentGroupChat(
        agents=agents,
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=agent_reviewer,
            function=selection_function,
            kernel=kernel,
            result_parser=parse_selection_result,
            history_variable_name="lastmessage",
            history_reducer=history_reducer,
        ),
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[agent_reviewer],  # Only the reviewer can determine if content is satisfactory
            function=termination_function,
            kernel=kernel,
            result_parser=parse_termination_result,
            history_variable_name="lastmessage",
            maximum_iterations=MAX_ITERATIONS,
            history_reducer=history_reducer,
        ),
    )


async def process_file_input(user_input: str) -> Optional[str]:
    """
    Processes file-based input when a user provides a filename with @ prefix.
    
    This function attempts to load content from a file in the script's directory
    when the user input starts with '@'. It handles file access errors gracefully.
    
    Args:
        user_input: The user's input string, potentially containing a file reference
        
    Returns:
        Optional[str]: The file contents if successful, None if file access failed
    """
    if not (user_input.startswith("@") and len(user_input) > 1):
        return None
        
    file_name = user_input[1:]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    try:
        if not os.path.exists(file_path):
            print(f"Unable to access file: {file_path}")
            return None
            
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {file_path}. Error: {str(e)}")
        return None


async def run_chat_loop(chat: AgentGroupChat) -> None:
    """
    Runs the interactive chat loop for user interaction with the agent group.
    
    This function handles:
    - Processing user input
    - Managing special commands (exit, reset)
    - Loading content from files
    - Displaying agent responses
    - Error handling during chat invocation
    
    Args:
        chat: The configured agent group chat to use for the conversation
    """
    print(
        "Ready! Type your input, or 'exit' to quit, 'reset' to restart the conversation. "
        "You may pass in a file path using @<path_to_file>, for example @WomensSuffrage.txt"
    )

    is_complete = False
    while not is_complete:
        print()
        user_input = input("User > ").strip()
        
        # Skip empty inputs
        if not user_input:
            continue

        # Handle exit command
        if user_input.lower() == "exit":
            is_complete = True
            break

        # Handle reset command
        if user_input.lower() == "reset":
            await chat.reset()
            print("[Conversation has been reset]")
            continue

        # Process file input if applicable
        file_content = await process_file_input(user_input)
        if file_content is not None:
            user_input = file_content

        # Add the user input to the chat
        await chat.add_chat_message(message=user_input)
        try:
            index = 1
            async for response in chat.invoke():
                print(f"\n" + "-" * 50 + f"\nResponse turn #{index}")
                if response is None or not response.name:
                    continue
                print()
                print(f"# {response.name.upper()}:\n{response.content}")
                index += 1
        except Exception as e:
            print(f"Error during chat invocation: {str(e)}")

        # Reset the chat's complete flag for the next conversation round
        chat.is_complete = False


async def main() -> None:
    """
    Main function that orchestrates the agent group chat system.
    
    This function:
    1. Creates the Semantic Kernel instance
    2. Sets up the specialized agents
    3. Configures the agent group chat with selection and termination strategies
    4. Runs the interactive chat loop
    """
    # Create a single shared kernel instance to orchestrate all agents
    kernel = create_kernel()
    
    # Create the specialized agents
    agents = create_agents(kernel)
    
    # Configure the agent group chat
    chat = create_agent_group_chat(kernel, agents)
    
    # Run the interactive chat loop
    await run_chat_loop(chat)


if __name__ == "__main__":
    asyncio.run(main())
