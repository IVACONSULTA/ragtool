"""
CrewAI RAG Agent Server

CrewAI-powered insurance policy agent that uses RAG (Retrieval Augmented Generation)
to answer questions about policy coverage and waiting periods.

Simple HTTP server that provides a /chat endpoint for direct access to the CrewAI agent.

Endpoints:
- GET /health - Health check
- POST /chat { message: string } - Send message to CrewAI RAG agent
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import nest_asyncio
import yaml
from crewai import LLM, Agent, Crew, Task
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from flask import Flask, jsonify, request  # pyright: ignore[reportMissingImports]
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from agents.utils.config import (
    get_data_path,
    get_llm_config,
    get_rag_config,
    print_config_info,
)
from agents.crewai.crew_entities import IVAConsultaCrew, CustomLlm, CustomRagTool

nest_asyncio.apply()

# Load environment variables if present
load_dotenv()


def load_agents_from_yaml(yaml_file: str) -> dict:
    """Load agent configurations from YAML file."""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"❌ Error loading agents from {yaml_file}: {e}")
        return {}


def load_tasks_from_yaml(yaml_file: str) -> dict:
    """Load task configurations from YAML file."""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"❌ Error loading tasks from {yaml_file}: {e}")
        return {}


def create_agent_from_config(agent_config: dict, llm: LLM, tools: list = None) -> Agent:
    """Create a CrewAI Agent from configuration dictionary."""
    return Agent(
        role=agent_config.get('role', ''),
        goal=agent_config.get('goal', ''),
        backstory=agent_config.get('backstory', ''),
        llm=llm,
        tools=tools or [],
        verbose=True,
        allow_delegation=False,
        max_retry_limit=5,
    )


def create_task_from_config(task_config: dict, agent: Agent) -> Task:
    """Create a CrewAI Task from configuration dictionary."""
    return Task(
        description=task_config.get('description', ''),
        expected_output=task_config.get('expected_output', ''),
        agent=agent,
    )

railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
railway_private_domain = os.getenv("RAILWAY_PRIVATE_DOMAIN")

app = Flask(__name__)

CORS(
    app,
    origins=[
        "http://localhost:8003",  # Local development
        f"https://{railway_public_domain}"  # Railway Public Domain
        f"https://{railway_private_domain}",  # Railway Private Domain
    ],
)

limiter = Limiter(
    get_remote_address, app=app, default_limits=["100 per hour", "10 per minute"]
)

#################################################################################
#                    RAG tool initialization                                    #
#################################################################################

# Initialize configuration using centralized config utility

# This line is no longer needed as we added the correct path above

try:
    # Initialize LLM with configuration
    print_config_info()

    llm_config = get_llm_config()

    print(f"LLM configuration: {llm_config}")

    llm_model = llm_config["llm_model"]
    llm_provider = llm_config["llm_provider"]
    llm_max_tokens = llm_config["llm_max_tokens"]
    llm = LLM(model=f"{llm_provider}/{llm_model}", max_tokens=llm_max_tokens)


except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("🔄 Using fallback llm configuration...")
    # Fallback configuration
    llm_fallback_config = {
        "llm_model": "gpt-4o-mini",
        "llm_provider": "openai",
        "llm_max_tokens": 1024,
    }
    llm_fallback_model = llm_fallback_config["llm_model"]
    llm_fallback_provider = llm_fallback_config["llm_provider"]
    llm_fallback_max_tokens = llm_fallback_config["llm_max_tokens"]
    llm = LLM(
        model=f"{llm_fallback_provider}/{llm_fallback_model}",
        max_tokens=llm_fallback_max_tokens,
    )

# Initialize RAG tool - try to load existing ChromaDB first
try:
    rag_config = get_rag_config()

    print(f"RagTool configuration: {rag_config}")

    # Configure persistent storage path using centralized config
    from agents.utils.config import get_storage_path

    storage_path = get_storage_path()

    # Import PDF processor for database management
    from agents.rag.files_ragtool import FilesRagTool

    processor = FilesRagTool(rag_config, storage_path)

    # Try to load existing ChromaDB first
    raw_rag_tool = processor.get_rag_tool()

    if raw_rag_tool is None:
        # No existing database, process PDFs for the first time
        print("🔄 No existing RagTool found. Processing PDFs for the first time...")
        data_path = get_data_path()  # Using centralized config function

        if os.path.exists(data_path):
            success = processor.initialize_ragtool_and_process_files([data_path])
            if success:
                raw_rag_tool = processor.rag_tool
                print(f"✅ Successfully processed and loaded PDF: {data_path}")
            else:
                print("❌ Failed to process PDF files")
                raw_rag_tool = None
        else:
            print(f"⚠️  PDF file not found: {data_path}")
            raw_rag_tool = None
    else:
        print("✅ Successfully loaded existing RagTool - no reprocessing needed")

    # Wrap the RAG tool for CrewAI compatibility
    if raw_rag_tool is not None:
        from agents.rag.rag_wrapper import create_rag_wrapper

        rag_tool = create_rag_wrapper(raw_rag_tool)
        print("🔧 RAG tool wrapped for CrewAI compatibility")
    else:
        rag_tool = None

except Exception as e:
    print(f"⚠️  Warning: Could not initialize RAGTool: {e}")
    print("🔄 Agent will continue without RAG capabilities")
    rag_tool = None

# Load agents and tasks from YAML files
agents_dir = Path(__file__).parent
agents_config = load_agents_from_yaml(agents_dir / "agents.yaml")
tasks_config = load_tasks_from_yaml(agents_dir / "tasks.yaml")

print(f"📋 Loaded {len(agents_config)} agents from YAML")
print(f"📋 Loaded {len(tasks_config)} tasks from YAML")

# Initialize IVA Consulta crew with custom LLM and RAG tool
try:
    custom_llm = CustomLlm()
    custom_rag_tool = CustomRagTool()
    iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
    print("✅ IVA Consulta crew initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize IVA Consulta crew: {e}")
    iva_consulta_crew = None


#################################################################################
#                             Helper functions                                  #
#################################################################################


def is_running_locally() -> bool:
    """Detect if running locally vs on Railway."""
    # Railway sets specific environment variables
    railway_env = os.getenv("RAILWAY_ENVIRONMENT_NAME")
    railway_service = os.getenv("RAILWAY_SERVICE_NAME")

    # Check if both environment variables are present and not empty
    if not railway_env or not railway_service:
        print("🏠 Local development detected - Railway env vars not set")
        return True

    # Check if the environment variables are not just empty strings
    if railway_env.strip() == "" or railway_service.strip() == "":
        print("🏠 Local development detected - Railway env vars are empty")
        return True

    # If Railway-specific vars are present and not empty, we're on Railway
    print("🔄 Railway environment detected:")
    print(f"✅  - RAILWAY_ENVIRONMENT_NAME: '{railway_env}'")
    print(f"✅  - RAILWAY_SERVICE_NAME: '{railway_service}'")
    return False


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


async def call_crewai_agent(user_message: str, agent_type: str = "iva_consulta_agent") -> str:
    """Call the CrewAI agent with the user's question."""
    try:
        print(f"📝 Processing question with {agent_type}: {user_message}")

        # Use IVA Consulta crew if available and agent type is iva_consulta_agent
        if agent_type == "iva_consulta_agent" and iva_consulta_crew is not None:
            print("🤖 Using IVA Consulta crew...")
            crew = iva_consulta_crew.create_crew_with_message(user_message)
            task_output = await crew.kickoff_async()
            response_content = str(task_output)
            
            # Ensure response is within 600 characters for IVA Consulta
            if len(response_content) > 600:
                response_content = response_content[:597] + "..."
                print(f"⚠️  Response truncated to 600 characters for IVA Consulta agent")
            
            print(f"✅ IVA Consulta response generated: {len(response_content)} characters")
            return response_content

        # Fallback to original method for other agent types
        # Determine tools to use based on RAG availability
        tools = [rag_tool] if rag_tool else []
        if not tools:
            print("⚠️  No RAG tool available - agent will use base knowledge only")

        # Get agent configuration
        agent_config = agents_config.get(agent_type)
        if not agent_config:
            raise ValueError(f"Agent type '{agent_type}' not found in configuration")

        # Create agent from configuration
        agent = create_agent_from_config(agent_config, llm, tools)
        agent.verbose = is_running_locally()  # Only verbose in local development
        agent.max_iterations = 10  # Default is 20

        # Get task configuration
        task_key = f"{agent_type}_task" if agent_type == "iva_consulta_agent" else "vat_consultation_task"
        task_config = tasks_config.get(task_key)
        if not task_config:
            # Fallback to generic task
            task_config = {
                "description": user_message,
                "expected_output": "A comprehensive response to the user's question"
            }

        # Create task from configuration
        task = create_task_from_config(task_config, agent)
        # Override description with user message for dynamic content
        task.description = user_message

        crew = Crew(
            agents=[agent], tasks=[task], verbose=is_running_locally()
        )

        print("🤖 Executing CrewAI task...")
        task_output = await crew.kickoff_async()

        response_content = str(task_output)
        
        # For IVA Consulta agent, ensure response is within 600 characters
        if agent_type == "iva_consulta_agent" and len(response_content) > 600:
            response_content = response_content[:597] + "..."
            print(f"⚠️  Response truncated to 600 characters for IVA Consulta agent")
        
        print(f"✅ {agent_type} response generated: {len(response_content)} characters")

        return response_content

    except Exception as e:
        error_msg = f"Error in CrewAI agent: {e}"
        print(f"❌ {error_msg}")

        # Return user-friendly error message
        if is_running_locally():
            raise e
        else:
            raise Exception(
                "CrewAI agent service is currently unavailable. Please try again later."
            )


#################################################################################
#                             Endpoints                                         #
#################################################################################


@app.route("/health", methods=["GET"])
def health():
    # Health endpoint can be accessed without API key for monitoring
    environment_type = "LOCAL" if is_running_locally() else "RAILWAY"
    data_path = get_data_path()

    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": "CrewAI RAG Agent Server",
            "version": "1.0.0",
            "environment": environment_type,
            "data_file": data_path,
            "rag_enabled": rag_tool is not None,
            "description": f"CrewAI insurance policy agent running on {environment_type}",
        }
    )


@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    # Check API key in production
    api_key, auth_error = verify_api_key()
    if auth_error:
        return auth_error
    try:
        data = request.get_json(force=True, silent=False)
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message: str = data["message"]
        agent_type: str = data.get("agent_type", "iva_consulta_agent")  # Default to IVA Consulta
        print(f"Received message: {user_message} (agent: {agent_type})")

        # Execute the CrewAI agent call
        result: str = asyncio.run(call_crewai_agent(user_message, agent_type))

        return jsonify(
            {
                "response": result,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as exc:
        print(f"Error in chat endpoint: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.route("/iva-consulta", methods=["POST"])
@limiter.limit("10 per minute")
def iva_consulta_chat():
    """IVA Consulta specific endpoint for VAT consultation."""
    # Check API key in production
    api_key, auth_error = verify_api_key()
    if auth_error:
        return auth_error
    try:
        data = request.get_json(force=True, silent=False)
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message: str = data["message"]
        print(f"Received IVA Consulta message: {user_message}")

        # Execute the IVA Consulta agent call
        result: str = asyncio.run(call_crewai_agent(user_message, "iva_consulta_agent"))

        return jsonify(
            {
                "response": result,
                "agent_type": "iva_consulta_agent",
                "timestamp": datetime.now().isoformat(),
                "source": "IVA Consulta VAT Specialist",
            }
        )
    except Exception as exc:
        print(f"Error in IVA Consulta endpoint: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "server": "CrewAI RAG Agent Server",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health", 
                "chat": "/chat",
                "iva_consulta": "/iva-consulta"
            },
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "description": "CrewAI-powered multi-agent system with RAG capabilities - Default: IVA Consulta VAT Specialist",
            "default_agent": "iva_consulta_agent",
            "agents": {
                "iva_consulta_agent": "VAT and indirect taxation specialist (DEFAULT)",
                "senior_coverage_assistant": "Insurance coverage specialist",
                "senior_sap_consultant": "SAP consulting specialist"
            }
        }
    )


#################################################################################
#                  __Main__      function                                       #
#################################################################################

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.getenv("PORT", 8001))

    environment_type = "LOCAL" if is_running_locally() else "RAILWAY"
    data_path = get_data_path()

    print("🚀 Starting CrewAI RAG Agent Server...")
    print(f"🌍 Environment: {environment_type}")
    print(f"📍 Server will be available on port: {port}")
    print("🔗 Health check: /health")
    print("💬 Chat endpoint: /chat")
    print("🏛️  IVA Consulta endpoint: /iva-consulta")
    print("🤖 CrewAI multi-agent system ready")
    print(f"📄 VAT documents: {data_path}")
    print("🎯 Default agent: IVA Consulta VAT Specialist")
    if rag_tool:
        print("✅ RAG capabilities enabled")
    else:
        print("⚠️  RAG capabilities disabled - using base knowledge only")
    print('\n💡 Send POST requests to /chat with JSON: {"message": "your question"}')
    print("⏹️  Press Ctrl+C to stop the server\n")

    try:
        # Use debug=False for production
        debug_mode = is_running_locally()
        print(f"🔄 Starting Flask app on host=0.0.0.0, port={port}, debug={debug_mode}")
        app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise
