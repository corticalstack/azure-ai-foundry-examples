# Tracing Project-Based Model Inference

This example demonstrates how to set up tracing for Azure AI Foundry project-based model inference. Tracing allows you to monitor and analyze your AI model's performance, usage patterns, and content generation.

## Prerequisites

- An Azure AI Foundry project with a model deployment
- An Application Insights resource in Azure
- The Azure AI Foundry project connection string

## Setting Up Tracing in the Azure AI Foundry Portal

1. Navigate to your Azure AI Foundry project in the Azure portal
2. Select the "Tracing" option in the project settings
3. Connect an existing Application Insights resource to your project, or create one in-situ.

## How Tracing is Implemented in the Code

The tracing implementation in `03-project-based-model-inference-chat-client/app.py` follows these steps:

### 1. Import Required Libraries

```python
from azure.core.settings import settings
from azure.ai.inference.tracing import AIInferenceInstrumentor 
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.trace import get_tracer
```

### 2. Configure Tracing Settings

```python
# Enable content recording for AI inference
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true"

# Set the tracing implementation to OpenTelemetry
settings.tracing_implementation = "opentelemetry"

# Instrument the AI Inference API
AIInferenceInstrumentor().instrument()

# Create a tracer for this module
tracer = get_tracer(__name__)
```

### 3. Connect to Application Insights

In the `initialize_client` function:

```python
# Get the Application Insights connection string from the project
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    logger.warning(
        "No application insights configured, telemetry will not be logged to project."
    )
   
# Configure Azure Monitor with the connection string
configure_azure_monitor(connection_string=application_insights_connection_string)
```

### 4. Clean Up Resources

When the application exits:

```python
if __name__ == "__main__":
    try:
        main()
        # Uninstrument the AI Inference API
        AIInferenceInstrumentor().uninstrument()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
```

## Key Components Explained

1. **Content Recording**: Setting `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` to "true" enables recording of the AI-generated content, which is useful for analysis and debugging.

2. **OpenTelemetry Integration**: The code uses OpenTelemetry as the tracing implementation, which is an industry-standard for observability.

3. **AIInferenceInstrumentor**: This class instruments the Azure AI Inference API to capture telemetry data automatically.

4. **Application Insights Connection**: The code retrieves the Application Insights connection string from the project client and configures Azure Monitor to send telemetry data to Application Insights.

## Additional Resources

For more information on tracing with Azure AI Foundry, see the [official documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/trace-local-sdk?tabs=python).

Note: The implementation in this example represents a working configuration that has been tested with Azure AI Foundry. While the official documentation provides general guidance, the specific implementation in `app.py` has been verified to work correctly.
