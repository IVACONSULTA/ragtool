"""
CrewAI RAG Agent Server

CrewAI-powered insurance policy agent that uses RAG (Retrieval Augmented Generation)
to answer questions about policy coverage and waiting periods.

Simple HTTP server that provides a /chat endpoint for direct access to the CrewAI agent.

Endpoints:
- GET /health - Health check
- POST /chat { message: string, agent_type?: string, context_country?: string } - Send message to CrewAI RAG agent
"""

import asyncio
import io
import os
import sys
import threading
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import nest_asyncio

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import custom agent types
from agents.crewai.crew_entities import (
    CustomLlm,
    CustomRagTool,
    IVAConsultaCrew,
    SapCrew,
    is_running_locally,
)

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
# Import compliance guardrails from guardrails package
from agents.guardrails.compliance_guardrails import (
    ComplianceViolationError,
    validate_all_compliance_rules,
)

# Import LangSmith integration
from agents.langsmith_integration import (
    get_langsmith_manager,
    log_agent_interaction,
    log_error,
    log_monitoring_summary,
    trace_async_function,
    trace_function,
)
from agents.utils.config import get_data_path

#asyncio.apply()
nest_asyncio.apply()

# Load environment variables if present
load_dotenv()

# Configure CrewAI to automatically show execution traces without prompting
# This ensures continuous logging without blocking on user input
os.environ.setdefault("CREWAI_TRACING_ENABLED", "true")
# Disable interactive prompts by setting a default response
# We'll mock stdin to automatically answer 'y' to continue logging

railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
railway_private_domain = os.getenv("RAILWAY_PRIVATE_DOMAIN")

app = Flask(__name__)

# Build CORS origins list, filtering out None values
cors_origins = ["http://localhost:8003"]  # Local development
if railway_public_domain:
    cors_origins.append(f"https://{railway_public_domain}")
if railway_private_domain:
    cors_origins.append(f"https://{railway_private_domain}")

CORS(app, origins=cors_origins)

limiter = Limiter(
    get_remote_address, app=app, default_limits=["100 per hour", "20 per minute"]
)

#################################################################################
#                    Initialization State Management                            #
#################################################################################

# Global initialization state
initialization_complete = False
initialization_error = None
initialization_status = "starting"

# Global variables for initialized components
custom_llm = None
custom_rag_tool = None
iva_consulta_crew = None
sap_crew = None
active_crew = None
langsmith_manager = None

#################################################################################
#                    Agent Initialization                                       #
#################################################################################

# Read agent role and data path from environment
AGENT_ROLE = os.getenv("AGENT_ROLE", "VAT_AGENT")  # Default: VAT_AGENT
# Normalize to lowercase for internal use
AGENT_ROLE = AGENT_ROLE.lower() if AGENT_ROLE else "vat_agent"

# Read RAG_DATA_PATH from environment (can be a directory or file path)
RAG_DATA_PATH_ENV = os.getenv("RAG_DATA_PATH")

# Define role-specific data paths if RAG_DATA_PATH not provided
ROLE_DATA_PATHS = {
    "vat_agent": "./data/raw",  # VAT agent
    "sap_agent": "./data/raw_sap",  # SAP agent
}

# Get data path: env var > role-based default > config default
# Note: RAG_DATA_PATH from env is used as directory, config.get_data_path() returns full file path
if RAG_DATA_PATH_ENV:
    # Use RAG_DATA_PATH from environment as directory
    RAG_DATA_PATH = RAG_DATA_PATH_ENV
    print(f"\n\n📁 Using data path from RAG_DATA_PATH env var: {RAG_DATA_PATH}")
elif AGENT_ROLE in ROLE_DATA_PATHS:
    # Use role-based default directory
    RAG_DATA_PATH = ROLE_DATA_PATHS.get(AGENT_ROLE)
    print(f"📁 Using role-based data path for '{AGENT_ROLE}': {RAG_DATA_PATH}")
else:
    # Unknown role - get directory from config (config.get_data_path() returns full file path)
    config_file_path = get_data_path()
    # Extract directory from full file path
    RAG_DATA_PATH = os.path.dirname(config_file_path) if os.path.isfile(config_file_path) else config_file_path
    print(
        f"📁 Unknown role '{AGENT_ROLE}', using config default path: {RAG_DATA_PATH}"
    )

print(f"🎯 Agent Role: {AGENT_ROLE.upper()}")
print(f"📂 Data Path: {RAG_DATA_PATH}")


def initialize_agents_background():
    """Initialize all agents in a background thread to allow server to start immediately."""
    global initialization_complete, initialization_error, initialization_status
    global custom_llm, custom_rag_tool, iva_consulta_crew, sap_crew, active_crew, langsmith_manager
    global AGENT_ROLE
    
    try:
        initialization_status = "initializing_langsmith"
        print("\n🔄 Starting background initialization...")
        
        # Initialize LangSmith integration
        langsmith_manager = get_langsmith_manager()
        if langsmith_manager.is_enabled():
            print("✅ LangSmith tracing enabled")
        else:
            print("⚠️  LangSmith tracing disabled (set LANGSMITH_API_KEY to enable)")

        # Initialize CustomLlm instance
        initialization_status = "initializing_llm"
        try:
            print("\n\n🤖 Initializing Custom LLM...")
            custom_llm = CustomLlm()
            llm = custom_llm.initialize_llm()

            # Wrap LLM with LangSmith tracing if available
            if langsmith_manager.is_enabled():
                try:
                    print("🔍 Wrapping LLM with LangSmith tracing...")
                    # Set environment variables for automatic tracing
                    os.environ["LANGCHAIN_TRACING_V2"] = "true"

                    # Get config values with proper fallbacks
                    endpoint = langsmith_manager.config.get("endpoint")
                    api_key = langsmith_manager.config.get("api_key")
                    project = langsmith_manager.config.get("project")

                    if endpoint:
                        os.environ["LANGCHAIN_ENDPOINT"] = endpoint
                    else:
                        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

                    if api_key:
                        os.environ["LANGCHAIN_API_KEY"] = api_key
                    else:
                        print("⚠️  No LangSmith API key found, LLM tracing may not work")

                    if project:
                        os.environ["LANGCHAIN_PROJECT"] = project
                    else:
                        os.environ["LANGCHAIN_PROJECT"] = "rag-ivaconsulta-dev"

                    # Enable comprehensive monitoring
                    print("📊 Enabling comprehensive LLM monitoring...")
                    print("   - Cost tracking enabled")
                    print("   - Token usage monitoring enabled")
                    print("   - Performance metrics tracking enabled")
                    print("   - Error tracking enabled")

                    print("✅ LangSmith environment variables set for automatic LLM tracing")
                except Exception as e:
                    print(f"⚠️  Could not set up LLM tracing: {e}")

            print(f"✅ Custom LLM initialized successfully: {custom_llm.get_model_info()}")

        except Exception as e:
            print(f"❌ Error initializing Custom LLM: {e}")
            # Create fallback instance
            custom_llm = CustomLlm()
            custom_llm._initialize_fallback_llm()
            llm = custom_llm.get_llm()
            print(f"✅ Custom LLM fallback initialized: {custom_llm.get_model_info()}")

        # Initialize CustomRagTool instance with role-based data path
        initialization_status = "initializing_rag"
        print(f"\n\n🤖 Initializing Custom RAG Tool for '{AGENT_ROLE.upper()}' role...")
        custom_rag_tool = CustomRagTool(data_path=RAG_DATA_PATH)
        rag_tool = custom_rag_tool.initialize_rag_tool(data_path=RAG_DATA_PATH)
        print(f"✅ Custom RAG Tool initialized: {custom_rag_tool.get_status_info()}")

        # Initialize crew based on AGENT_ROLE (no fallback, no secondary crew)
        initialization_status = "initializing_crew"
        
        # Initialize VAT Agent crew
        if AGENT_ROLE == "vat_agent":
            print("\n\n🤖 Initializing IVA Consulta Crew...")
            iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
            active_crew = iva_consulta_crew
            print("✅ IVA Consulta Crew initialized successfully")
            print(f"   - {custom_llm.get_model_info()}")
            print(f"   - {custom_rag_tool.get_status_info()}")

        # Initialize SAP Agent crew
        elif AGENT_ROLE == "sap_agent":
            print("\n\n🤖 Initializing SAP Crew...")
            sap_crew = SapCrew(custom_llm, custom_rag_tool)
            active_crew = sap_crew
            print("✅ SAP Crew initialized successfully")
            print(f"   - {custom_llm.get_model_info()}")
            print(f"   - {custom_rag_tool.get_status_info()}")

        # Unknown role - default to VAT Agent
        else:
            print(f"\n\n⚠️  Unknown AGENT_ROLE '{AGENT_ROLE}', defaulting to VAT Agent")
            AGENT_ROLE = "vat_agent"  # Normalize to known role
            print("🤖 Initializing IVA Consulta Crew (DEFAULT)...")
            iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
            active_crew = iva_consulta_crew
            print("✅ IVA Consulta Crew initialized successfully")
            print(f"   - {custom_llm.get_model_info()}")
            print(f"   - {custom_rag_tool.get_status_info()}")
        
        # Mark initialization as complete
        initialization_status = "ready"
        initialization_complete = True
        print("\n✅ Background initialization complete! Server is ready to handle requests.")
        
    except Exception as e:
        initialization_error = str(e)
        initialization_status = "failed"
        print(f"\n❌ Background initialization failed: {e}")
        import traceback
        traceback.print_exc()


#################################################################################
#                             Helper functions                                  #
#################################################################################


class AutoConfirmExecutionTraces:
    """Context manager to automatically answer 'y' to CrewAI's execution trace prompt.
    
    This ensures that execution traces continue to be logged without blocking on user input.
    CrewAI prompts with: "Would you like to view your execution traces? [y/N]"
    This function automatically answers 'y' to continue logging.
    """
    
    def __init__(self):
        self.stack = None
    
    def __enter__(self):
        # Patch both input() and sys.stdin to handle different CrewAI input methods
        # Most Python code uses input(), but we cover both cases
        def mock_input(prompt=""):
            # Automatically return 'y' for execution trace prompts
            if "execution traces" in prompt.lower() or "view" in prompt.lower():
                print("✅ Auto-confirming execution trace display (y)")
                return 'y'
            # For any other prompts, return 'y' as default
            return 'y'
        
        # Use ExitStack to properly manage multiple context managers
        self.stack = ExitStack()
        
        # Patch sys.stdin for direct stdin reads
        self.stack.enter_context(patch('sys.stdin', io.StringIO('y\n')))
        # Patch builtins.input for input() function calls
        self.stack.enter_context(patch('builtins.input', side_effect=mock_input))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stack:
            self.stack.close()
        return False


def auto_confirm_execution_traces():
    """Factory function that returns the AutoConfirmExecutionTraces context manager."""
    return AutoConfirmExecutionTraces()


def verify_api_key():
    """Verify API key for production environments and security testing."""
    # Check if security testing mode is enabled
    security_test_mode = os.getenv("SECURITY_TEST_MODE", "false").lower() == "true"

    if not is_running_locally() or security_test_mode:
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY")

        if not api_key:
            print("❌ No API key provided in request headers")
            return None, (
                jsonify({"error": "Unauthorized - Missing API key in request"}),
                401,
            )
        elif not expected_key:
            print("❌ No API key configured in environment")
            return None, (
                jsonify({"error": "Unauthorized - API key not configured"}),
                401,
            )
        elif api_key.strip() != expected_key.strip():  # Strip whitespace from both
            print("❌ API key mismatch")
            return None, (jsonify({"error": "Unauthorized - Invalid API key"}), 401)

        print("✅ API key verification successful")
        return api_key, None
    else:
        # Local development - no API key required
        print("🏠 Local development - skipping API key verification")
        return None, None



async def call_crewai_agent(
    user_message: str, agent_type: str = None, context_country: str = None
) -> str:
    """Call the CrewAI agent with the user's question.

    Args:
        user_message: The user's question/message
        agent_type: Optional agent type. If not provided, uses active_crew based on AGENT_ROLE
        context_country: Optional country context to provide jurisdictional context for the query

    Returns:
        The agent's response as a string

    Raises:
        ComplianceViolationError: If message violates EU AI Act compliance rules
        Exception: If agent is not available or other errors occur
    """
    # Check if any crew is available
    if active_crew is None:
        error_msg = "The agent is not available at the moment. Please try again later."
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

    try:
        print(f"📝 Processing question: {user_message}")

        # Apply EU AI Act compliance guardrails before processing
        print("🛡️ Running EU AI Act compliance checks...")
        is_compliant, compliance_result = validate_all_compliance_rules(user_message)

        if not is_compliant:
            print(f"❌ Compliance violation detected: {compliance_result}")

            # Log compliance violation to LangSmith
            log_error(
                ComplianceViolationError(compliance_result),
                "compliance_check",
                {"user_message": user_message, "violation": compliance_result},
            )

            raise ComplianceViolationError(compliance_result)

        print("✅ Message passed all compliance checks")

        # Select crew based on agent_type or use active_crew (initialized once at startup)
        selected_crew = None
        crew_name = ""

        if agent_type == "iva_consulta_agent" and iva_consulta_crew is not None:
            selected_crew = iva_consulta_crew
            crew_name = "IVA Consulta"
        elif agent_type == "sap_consultant" and sap_crew is not None:
            selected_crew = sap_crew
            crew_name = "SAP"
        else:
            # Use active_crew (initialized once based on AGENT_ROLE)
            selected_crew = active_crew
            crew_name = "IVA Consulta" if AGENT_ROLE == "vat_agent" else "SAP"

        if selected_crew is None:
            error_msg = (
                "The agent is not available at the moment. Please try again later."
            )
            print(f"❌ {error_msg}")
            raise Exception(error_msg)

        print(f"🤖 Using {crew_name} crew...")

        # Create crew instance with user message and execute
        print("🤖 Executing CrewAI task...")
        crew_instance = selected_crew.create_crew_with_message(
            user_message, context_country
        )
        
        # Trace the agent role execution if LangSmith is enabled
        # Use auto_confirm_execution_traces to automatically answer 'y' to prompts
        # This ensures execution traces continue logging without blocking
        with auto_confirm_execution_traces():
            if langsmith_manager.is_enabled():
                try:
                    from langsmith import trace
                    agent_trace_name = f"agent_{crew_name.lower().replace(' ', '_')}"
                    with trace(name=agent_trace_name, run_type="chain") as agent_run:
                        agent_run.inputs = {"user_message": user_message, "crew_name": crew_name}
                        if context_country:
                            agent_run.inputs["context_country"] = context_country
                        
                        task_output = await crew_instance.kickoff_async()
                        
                        agent_run.outputs = {"response": str(task_output)}
                except Exception as e:
                    print(f"⚠️  Could not trace agent execution: {e}")
                    # Fallback: execute without tracing
                    task_output = await crew_instance.kickoff_async()
            else:
                # Execute without tracing if LangSmith is disabled
                task_output = await crew_instance.kickoff_async()

        response_content = str(task_output)

        # For IVA Consulta agent, ensure response is within 600 characters
        if (
            agent_type == "iva_consulta_agent"
            or (agent_type is None and AGENT_ROLE == "vat_agent")
        ) and len(response_content) > 600:
            response_content = response_content[:597] + "..."
            print(f"⚠️  Response truncated to 600 characters for IVA Consulta agent")

        actual_agent_type = (
            agent_type
            if agent_type
            else (
                "iva_consulta_agent" if AGENT_ROLE == "vat_agent" else "sap_consultant"
            )
        )
        print(f"✅ Response generated: {len(response_content)} characters")

        # Log successful agent interaction to LangSmith
        log_agent_interaction(
            actual_agent_type,
            user_message,
            response_content,
            {
                "compliance_checked": True,
                "response_length": len(response_content),
                "context_country": context_country if context_country else None,
            },
        )

        # Log monitoring summary if LangSmith is enabled
        if langsmith_manager.is_enabled():
            print("\n📊 Current LLM Usage Summary:")
            log_monitoring_summary()

        return response_content

    except ComplianceViolationError:
        # Re-raise compliance violations as-is
        raise
    except Exception as e:
        error_msg = f"Error in CrewAI agent: {e}"
        print(f"❌ {error_msg}")

        # Log error to LangSmith
        log_error(
            e,
            "crewai_agent_execution",
            {
                "user_message": user_message,
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Return user-friendly error message
        if is_running_locally():
            raise e
        else:
            raise Exception(
                "The agent is not available at the moment. Please try again later."
            )


#################################################################################
#                             Endpoints                                         #
#################################################################################

@trace_function("call_health_endpoint")
@app.route("/health", methods=["GET"])
def health():
    # Health endpoint can be accessed without API key for monitoring
    environment_type = "LOCAL" if is_running_locally() else "RAILWAY"
    
    # Determine overall health status based on initialization
    if initialization_complete:
        status = "healthy"
        data_path = get_data_path()
    elif initialization_error:
        status = "unhealthy"
        data_path = "N/A"
    else:
        status = "initializing"
        data_path = "N/A"

    # Get LangSmith status (only if initialized)
    langsmith_status = {
        "enabled": langsmith_manager.is_enabled() if langsmith_manager else False,
        "project": langsmith_manager.config.get("project", "N/A") if langsmith_manager else "N/A",
        "client_available": langsmith_manager.get_client() is not None if langsmith_manager else False,
    }

    response_data = {
        "status": status,
        "initialization_status": initialization_status,
        "initialization_complete": initialization_complete,
        "timestamp": datetime.now().isoformat(),
        "server": "CrewAI RAG Agent Server",
        "version": "1.0.0",
        "environment": environment_type,
        "data_file": data_path,
        "rag_enabled": custom_rag_tool.is_available() if custom_rag_tool else False,
        "llm_model": custom_llm.get_model_info() if custom_llm else "Initializing...",
        "rag_status": (
            custom_rag_tool.get_status_info()
            if custom_rag_tool
            else "Initializing..."
        ),
        "langsmith": langsmith_status,
        "description": f"CrewAI insurance policy agent running on {environment_type}",
    }
    
    # Add error info if initialization failed
    if initialization_error:
        response_data["initialization_error"] = initialization_error
    
    return jsonify(response_data)

@trace_async_function("call_chat_endpoint")
@app.route("/chat", methods=["POST"])
@limiter.limit("15 per minute")
def chat():
    # Check if initialization is complete
    if not initialization_complete:
        if initialization_error:
            return jsonify({
                "error": "Server initialization failed",
                "details": initialization_error,
                "status": "unhealthy"
            }), 503
        else:
            return jsonify({
                "error": "Server is still initializing. Please try again in a moment.",
                "initialization_status": initialization_status,
                "status": "initializing"
            }), 503
    
    # Check API key in production
    api_key, auth_error = verify_api_key()
    if auth_error:
        return auth_error
    try:
        data = request.get_json(force=True, silent=False)
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message: str = data["message"]
        context_country: str = data.get("context_country", "Spain")
        # agent_type is optional - if not provided, uses active_crew based on AGENT_ROLE
        agent_type: str = data.get("agent_type")  # Can be None to use default
        # context_country is optional - provides country context for the query

        if agent_type:
            print(f"Received message: {user_message} (agent: {agent_type})")
        else:
            print(
                f"Received message: {user_message} (using default agent based on AGENT_ROLE: {AGENT_ROLE.upper()})"
            )

        if context_country:
            print(f"📍 Country context: {context_country}")

        # Execute the CrewAI agent call
        result: str = asyncio.run(
            call_crewai_agent(user_message, agent_type, context_country)
        )

        # Note: Agent interaction is already logged by call_crewai_agent() 
        # and endpoint is traced by @trace_async_function decorator above
        # No need for duplicate logging here

        # Determine actual agent type for response
        actual_agent_type = (
            agent_type
            if agent_type
            else (
                "iva_consulta_agent" if AGENT_ROLE == "vat_agent" else "sap_consultant"
            )
        )

        return jsonify(
            {
                "response": result,
                "agent_type": actual_agent_type,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as exc:
        print(f"❌ Error in chat endpoint: {exc}")

        # Log error to LangSmith
        if langsmith_manager.is_enabled():
            log_error(
                exc,
                "chat_endpoint",
                {
                    "user_message": (
                        data.get("message", "N/A") if "data" in locals() else "N/A"
                    ),
                    "error_type": type(exc).__name__,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        return jsonify({"error": str(exc)}), 500

@trace_async_function("call_index_endpoint")
@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "server": "CrewAI RAG Agent Server with Guardrails",
            "version": "1.0.0",
            "endpoints": {"health": "/health", "chat": "/chat"},
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "description": "CrewAI-powered multi-agent system with RAG capabilities and EU AI Act compliance - Default: IVA Consulta VAT Specialist",
            "default_agent": "iva_consulta_agent",
            "guardrails": "EU AI Act compliance enabled",
            "agents": {
                "iva_consulta_agent": "VAT and indirect taxation specialist (DEFAULT)",
                "sap_consultant": "SAP consulting specialist",
                "senior_coverage_assistant": "Insurance coverage specialist",
            },
        }
    )


#################################################################################
#                  __Main__      function                                       #
#################################################################################

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run and Railway set this automatically)
    port = int(os.getenv("PORT", 8001))

    environment_type = "LOCAL" if is_running_locally() else "RAILWAY"

    print("🚀 Starting CrewAI RAG Agent Server with Guardrails...\n")
    print(f"🌍 Environment: {environment_type}")
    print(f"📍 Server will be available on port: {port}")
    print("🔗 Health check: /health")
    print("💬 Chat endpoint: /chat")
    
    agent_type_name = (
        "IVA Consulta VAT Specialist"
        if AGENT_ROLE == "vat_agent"
        else "SAP Consultant"
    )
    print(f"🎯 Default agent: {AGENT_ROLE.upper()} ({agent_type_name})")
    print(f"📂 Using data path: {RAG_DATA_PATH}")
    print("🛡️  EU AI Act compliance guardrails enabled")
    print('\n💡 Send POST requests to /chat with JSON: {"message": "your question"}')
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    # Start background initialization thread
    print("🔄 Starting background initialization thread...")
    print("⚡ Server will start immediately and accept health checks")
    print("⏳ Agent initialization will continue in the background\n")
    
    init_thread = threading.Thread(target=initialize_agents_background, daemon=True)
    init_thread.start()

    try:
        # Use debug=False for production and to avoid ChromaDB lock issues
        # Debug mode causes Flask to reload, which can cause ChromaDB resource conflicts
        debug_mode = False  # Disabled to prevent ChromaDB lock issues
        use_reloader = False  # Explicitly disable reloader
        print(f"✅ Starting Flask app on host=0.0.0.0, port={port}, debug={debug_mode}")
        print(f"✅ Server is now listening and ready for healthchecks!")
        print(f"⏳ Agent initialization continues in background...\n")
        app.run(
            host="0.0.0.0",
            port=port,
            debug=debug_mode,
            use_reloader=use_reloader,
            threaded=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise
