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
import os
import sys
from datetime import datetime

import nest_asyncio

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Import custom agent types
from agents.crewai.crew_entities import CustomLlm, CustomRagTool, SapCrew, IVAConsultaCrew, is_running_locally

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from agents.utils.config import get_data_path

# Import compliance guardrails from guardrails package
from agents.guardrails.compliance_guardrails import (
    ComplianceViolationError,
    validate_all_compliance_rules,
)

# Import LangSmith integration
from agents.langsmith_integration import (
    get_langsmith_manager,
    trace_async_function,
    log_agent_interaction,
    log_error,
    log_monitoring_summary,
)

nest_asyncio.apply()

# Load environment variables if present
load_dotenv()

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
#                    Agent Initialization                                       #
#################################################################################

# Read RAG role and data path from environment
RAG_ROLE = os.getenv("RAG_ROLE", "iva_consulta").lower()  # Default: iva_consulta
RAG_DATA_PATH = os.getenv("RAG_DATA_PATH")  # Optional: can be None to use config default

# Define role-specific data paths if RAG_DATA_PATH not provided
ROLE_DATA_PATHS = {
    "iva_consulta": "./data/raw",  # VAT documents directory
    "vat_agent": "./data/raw",  # VAT agent (alias for iva_consulta)
    "sap": "./data/raw_sap",  # SAP documents directory
}

# Get data path: env var > role-based default > config default
if RAG_DATA_PATH is None:
    RAG_DATA_PATH = ROLE_DATA_PATHS.get(RAG_ROLE)
    if RAG_DATA_PATH is None:
        # Unknown role - use config default
        RAG_DATA_PATH = get_data_path()
        print(f"📁 Unknown role '{RAG_ROLE}', using config default path: {RAG_DATA_PATH}")
    else:
        print(f"📁 Using role-based data path for '{RAG_ROLE}': {RAG_DATA_PATH}")
else:
    print(f"📁 Using custom data path from RAG_DATA_PATH: {RAG_DATA_PATH}")

print(f"🎯 RAG Role: {RAG_ROLE}")
print(f"📂 Data Path: {RAG_DATA_PATH}")

# Initialize LangSmith integration
print("🔍 Initializing LangSmith integration...")
langsmith_manager = get_langsmith_manager()
if langsmith_manager.is_enabled():
    print("✅ LangSmith tracing enabled")
else:
    print("⚠️  LangSmith tracing disabled (set LANGSMITH_API_KEY to enable)")

# Initialize CustomLlm instance
try:
    print("🤖 Initializing Custom LLM...")
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
                os.environ["LANGCHAIN_PROJECT"] = "ivaconsulta-rag-tool"
            
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
try:
    print(f"🤖 Initializing Custom RAG Tool for '{RAG_ROLE}' role...")
    custom_rag_tool = CustomRagTool(data_path=RAG_DATA_PATH)
    rag_tool = custom_rag_tool.initialize_rag_tool(data_path=RAG_DATA_PATH)
    print(f"✅ Custom RAG Tool initialized: {custom_rag_tool.get_status_info()}")
except Exception as e:
    print(f"❌ Error initializing Custom RAG Tool: {e}")
    # Create fallback instance
    custom_rag_tool = CustomRagTool(data_path=RAG_DATA_PATH)
    rag_tool = None
    print("✅ Custom RAG Tool fallback initialized: RAG Tool: DISABLED")

# Initialize crews based on RAG_ROLE
# These crews are initialized once at startup
iva_consulta_crew = None
sap_crew = None
active_crew = None  # The active crew to use for requests

# Initialize crews based on RAG_ROLE
# The active_crew will be used as the default for all requests

# Initialize IVA Consulta crew (default)
if RAG_ROLE in ["iva_consulta", "vat_agent"]:
    try:
        print("🤖 Initializing IVA Consulta Crew (DEFAULT)...")
        iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
        active_crew = iva_consulta_crew
        print("✅ IVA Consulta Crew initialized successfully")
        print(f"   - {custom_llm.get_model_info()}")
        print(f"   - {custom_rag_tool.get_status_info()}")
    except Exception as e:
        print(f"❌ Error initializing IVA Consulta Crew: {e}")
        print("🔄 Attempting to initialize SAP Crew as fallback...")
        # Reinitialize RAG tool with SAP data path for fallback
        fallback_data_path = ROLE_DATA_PATHS.get("sap")
        if fallback_data_path:
            print(f"🔄 Reinitializing RAG tool with SAP data path: {fallback_data_path}")
            try:
                custom_rag_tool.refresh_rag_tool(data_path=fallback_data_path)
                print(f"✅ RAG tool reinitialized with SAP data path")
            except Exception as rag_error:
                print(f"⚠️  Could not reinitialize RAG tool: {rag_error}")
        
        try:
            sap_crew = SapCrew(custom_llm, custom_rag_tool)
            active_crew = sap_crew
            print("✅ SAP Crew initialized as fallback")
        except Exception as fallback_error:
            print(f"❌ Fallback initialization also failed: {fallback_error}")
            active_crew = None

# Initialize SAP crew (default)
elif RAG_ROLE == "sap":
    try:
        print("🤖 Initializing SAP Crew (DEFAULT)...")
        sap_crew = SapCrew(custom_llm, custom_rag_tool)
        active_crew = sap_crew
        print("✅ SAP Crew initialized successfully")
        print(f"   - {custom_llm.get_model_info()}")
        print(f"   - {custom_rag_tool.get_status_info()}")
    except Exception as e:
        print(f"❌ Error initializing SAP Crew: {e}")
        print("🔄 Attempting to initialize IVA Consulta Crew as fallback...")
        # Reinitialize RAG tool with IVA Consulta data path for fallback
        fallback_data_path = ROLE_DATA_PATHS.get("iva_consulta")
        if fallback_data_path:
            print(f"🔄 Reinitializing RAG tool with IVA Consulta data path: {fallback_data_path}")
            try:
                custom_rag_tool.refresh_rag_tool(data_path=fallback_data_path)
                print(f"✅ RAG tool reinitialized with IVA Consulta data path")
            except Exception as rag_error:
                print(f"⚠️  Could not reinitialize RAG tool: {rag_error}")
        
        try:
            iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
            active_crew = iva_consulta_crew
            print("✅ IVA Consulta Crew initialized as fallback")
        except Exception as fallback_error:
            print(f"❌ Fallback initialization also failed: {fallback_error}")
            active_crew = None

else:
    print(f"⚠️  Unknown RAG_ROLE '{RAG_ROLE}', defaulting to IVA Consulta")
    RAG_ROLE = "iva_consulta"  # Normalize to known role
    try:
        print("🤖 Initializing IVA Consulta Crew (DEFAULT)...")
        iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
        active_crew = iva_consulta_crew
        print("✅ IVA Consulta Crew initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing IVA Consulta Crew: {e}")
        active_crew = None

# Initialize the other crew as well if not already initialized (for flexibility)
if RAG_ROLE == "iva_consulta" and sap_crew is None:
    try:
        print("🤖 Initializing SAP Crew (secondary)...")
        sap_crew = SapCrew(custom_llm, custom_rag_tool)
        print("✅ SAP Crew initialized successfully")
    except Exception as e:
        print(f"⚠️  Could not initialize SAP Crew (secondary): {e}")

elif RAG_ROLE == "sap" and iva_consulta_crew is None:
    try:
        print("🤖 Initializing IVA Consulta Crew (secondary)...")
        iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
        print("✅ IVA Consulta Crew initialized successfully")
    except Exception as e:
        print(f"⚠️  Could not initialize IVA Consulta Crew (secondary): {e}")




#################################################################################
#                             Helper functions                                  #
#################################################################################


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



@trace_async_function("call_crewai_agent")
async def call_crewai_agent(user_message: str, agent_type: str = None, context_country: str = None) -> str:
    """Call the CrewAI agent with the user's question.
    
    Args:
        user_message: The user's question/message
        agent_type: Optional agent type. If not provided, uses active_crew based on RAG_ROLE
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
                {"user_message": user_message, "violation": compliance_result}
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
            # Use active_crew (initialized once based on RAG_ROLE)
            selected_crew = active_crew
            crew_name = "IVA Consulta" if RAG_ROLE == "iva_consulta" else "SAP"
        
        if selected_crew is None:
            error_msg = "The agent is not available at the moment. Please try again later."
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        print(f"🤖 Using {crew_name} crew...")

        # Create crew instance with user message and execute
        print("🤖 Executing CrewAI task...")
        crew_instance = selected_crew.create_crew_with_message(user_message, context_country)
        task_output = await crew_instance.kickoff_async()

        response_content = str(task_output)
        
        # For IVA Consulta agent, ensure response is within 600 characters
        if (agent_type == "iva_consulta_agent" or 
            (agent_type is None and RAG_ROLE == "iva_consulta")) and len(response_content) > 600:
            response_content = response_content[:597] + "..."
            print(f"⚠️  Response truncated to 600 characters for IVA Consulta agent")
        
        actual_agent_type = agent_type if agent_type else (f"{RAG_ROLE}_agent" if RAG_ROLE == "iva_consulta" else "sap_consultant")
        print(f"✅ Response generated: {len(response_content)} characters")

        # Log successful agent interaction to LangSmith
        log_agent_interaction(
            actual_agent_type,
            user_message,
            response_content,
            {
                "compliance_checked": True,
                "response_length": len(response_content),
                "context_country": context_country if context_country else None
            }
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
                "timestamp": datetime.now().isoformat()
            }
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


@app.route("/health", methods=["GET"])
def health():
    # Health endpoint can be accessed without API key for monitoring
    environment_type = "LOCAL" if is_running_locally() else "RAILWAY"
    data_path = get_data_path()

    # Get LangSmith status
    langsmith_status = {
        "enabled": langsmith_manager.is_enabled(),
        "project": langsmith_manager.config.get("project", "N/A"),
        "client_available": langsmith_manager.get_client() is not None
    }

    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": "CrewAI RAG Agent Server",
            "version": "1.0.0",
            "environment": environment_type,
            "data_file": data_path,
            "rag_enabled": custom_rag_tool.is_available() if custom_rag_tool else False,
            "llm_model": custom_llm.get_model_info() if custom_llm else "Unknown",
            "rag_status": (
                custom_rag_tool.get_status_info()
                if custom_rag_tool
                else "RAG Tool: UNKNOWN"
            ),
            "langsmith": langsmith_status,
            "description": f"CrewAI insurance policy agent running on {environment_type}",
        }
    )


@app.route("/chat", methods=["POST"])
@limiter.limit("15 per minute")
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
        context_country: str = data.get("context_country", "Spain")
        # agent_type is optional - if not provided, uses active_crew based on RAG_ROLE
        agent_type: str = data.get("agent_type")  # Can be None to use default
        # context_country is optional - provides country context for the query
        
        if agent_type:
            print(f"Received message: {user_message} (agent: {agent_type})")
        else:
            print(f"Received message: {user_message} (using default agent based on RAG_ROLE)")
        
        if context_country:
            print(f"📍 Country context: {context_country}")

        # Execute the CrewAI agent call
        result: str = asyncio.run(call_crewai_agent(user_message, agent_type, context_country))

        # Log successful chat interaction to LangSmith
        if langsmith_manager.is_enabled():
            log_agent_interaction(
                "chat_endpoint",
                user_message,
                result,
                {
                    "endpoint": "/chat",
                    "api_key_provided": api_key is not None,
                    "response_length": len(result),
                    "context_country": context_country if context_country else None,
                    "timestamp": datetime.now().isoformat()
                }
            )

        # Determine actual agent type for response
        actual_agent_type = agent_type if agent_type else (
            "iva_consulta_agent" if RAG_ROLE == "iva_consulta" else "sap_consultant"
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
                    "user_message": data.get("message", "N/A") if 'data' in locals() else "N/A",
                    "error_type": type(exc).__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )

        return jsonify({"error": str(exc)}), 500



@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "server": "CrewAI RAG Agent Server with Guardrails",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health", 
                "chat": "/chat"
            },
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "description": "CrewAI-powered multi-agent system with RAG capabilities and EU AI Act compliance - Default: IVA Consulta VAT Specialist",
            "default_agent": "iva_consulta_agent",
            "guardrails": "EU AI Act compliance enabled",
            "agents": {
                "iva_consulta_agent": "VAT and indirect taxation specialist (DEFAULT)",
                "sap_consultant": "SAP consulting specialist",
                "senior_coverage_assistant": "Insurance coverage specialist"
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

    print("🚀 Starting CrewAI RAG Agent Server with Guardrails...")
    print(f"🌍 Environment: {environment_type}")
    print(f"📍 Server will be available on port: {port}")
    print("🔗 Health check: /health")
    print("💬 Chat endpoint: /chat")
    print("🤖 CrewAI multi-agent system ready")
    print(f"📄 VAT documents: {data_path}")
    agent_type_name = 'IVA Consulta VAT Specialist' if RAG_ROLE in ['iva_consulta', 'vat_agent'] else 'SAP Consultant'
    print(f"🎯 Default agent: {RAG_ROLE.upper()} ({agent_type_name})")
    print(f"📂 Using data path: {RAG_DATA_PATH}")
    print("🛡️  EU AI Act compliance guardrails enabled")
    print(f"🧠 {custom_llm.get_model_info() if custom_llm else 'LLM: Unknown'}")
    if custom_rag_tool and custom_rag_tool.is_available():
        print("✅ RAG capabilities enabled")
    else:
        print("⚠️  RAG capabilities disabled - using base knowledge only")
    
    # LangSmith status
    if langsmith_manager.is_enabled():
        print(f"🔍 LangSmith tracing enabled for project: {langsmith_manager.config.get('project', 'N/A')}")
    else:
        print("⚠️  LangSmith tracing disabled (set LANGSMITH_API_KEY to enable)")

    print('\n💡 Send POST requests to /chat with JSON: {"message": "your question"}')
    print("⏹️  Press Ctrl+C to stop the server\n")

    try:
        # Use debug=False for production and to avoid ChromaDB lock issues
        # Debug mode causes Flask to reload, which can cause ChromaDB resource conflicts
        debug_mode = False  # Disabled to prevent ChromaDB lock issues
        use_reloader = False  # Explicitly disable reloader
        print(f"🔄 Starting Flask app on host=0.0.0.0, port={port}, debug={debug_mode}")
        app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=use_reloader, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise
