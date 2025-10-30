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
    create_traced_openai_client,
    log_monitoring_summary,
)

nest_asyncio.apply()

# Load environment variables if present
load_dotenv()

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
    get_remote_address, app=app, default_limits=["100 per hour", "20 per minute"]
)

#################################################################################
#                    Agent Initialization                                       #
#################################################################################

# Initialize configuration using centralized config utility


# This line is no longer needed as we added the correct path above

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
                os.environ["LANGCHAIN_PROJECT"] = "sap-rag-tool"
            
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

# Initialize CustomRagTool instance
try:
    print("🤖 Initializing Custom RAG Tool...")
    custom_rag_tool = CustomRagTool()
    rag_tool = custom_rag_tool.initialize_rag_tool()
    print(f"✅ Custom RAG Tool initialized: {custom_rag_tool.get_status_info()}")
except Exception as e:
    print(f"❌ Error initializing Custom RAG Tool: {e}")
    # Create fallback instance
    custom_rag_tool = CustomRagTool()
    rag_tool = None
    print("✅ Custom RAG Tool fallback initialized: RAG Tool: DISABLED")

# Initialize the IVA Consulta crew instance (DEFAULT)
try:
    print("🤖 Initializing IVA Consulta Crew (DEFAULT)...")
    iva_consulta_crew = IVAConsultaCrew(custom_llm, custom_rag_tool)
    print("✅ IVA Consulta Crew initialized successfully")
    print(f"   - {custom_llm.get_model_info()}")
    print(f"   - {custom_rag_tool.get_status_info()}")
except Exception as e:
    print(f"❌ Error initializing IVA Consulta Crew: {e}")
    print("🔄 Attempting to initialize SAP Crew as fallback...")
    try:
        iva_consulta_crew = SapCrew(custom_llm, custom_rag_tool)
        print("✅ SAP Crew fallback initialized successfully")
    except Exception as fallback_error:
        print(f"❌ Fallback initialization also failed: {fallback_error}")
        iva_consulta_crew = None

# Initialize the SAP crew instance (for compatibility)
try:
    print("🤖 Initializing SAP Crew...")
    sap_crew = SapCrew(custom_llm, custom_rag_tool)
    print("✅ SAP Crew initialized successfully")
except Exception as e:
    print(f"❌ Error initializing SAP Crew: {e}")
    sap_crew = None

# # Initialize the insurance crew instance
# try:
#     print("🤖 Initializing Insurance Crew...")
#     insurance_crew = InsuranceCrew(custom_llm, custom_rag_tool)
#     print("✅ Insurance Crew initialized successfully")
#     print(f"   - {custom_llm.get_model_info()}")
#     print(f"   - {custom_rag_tool.get_status_info()}")
# except Exception as e:
#     print(f"❌ Error initializing Insurance Crew: {e}")
#     insurance_crew = None



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
async def call_crewai_agent(user_message: str, agent_type: str = "iva_consulta_agent") -> str:
    """Call the CrewAI agent with the user's question."""
    try:
        print(f"📝 Processing question with {agent_type}: {user_message}")

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

        # Use IVA Consulta crew as default
        if agent_type == "iva_consulta_agent" and iva_consulta_crew is not None:
            print("🤖 Using IVA Consulta crew...")
            crew_instance = iva_consulta_crew.create_crew_with_message(user_message)
        elif agent_type == "sap_consultant" and sap_crew is not None:
            print("🤖 Using SAP crew...")
            crew_instance = sap_crew.create_crew_with_message(user_message)
        else:
            # Fallback to IVA Consulta crew if available
            if iva_consulta_crew is not None:
                print("🤖 Using IVA Consulta crew as fallback...")
                crew_instance = iva_consulta_crew.create_crew_with_message(user_message)
            elif sap_crew is not None:
                print("🤖 Using SAP crew as fallback...")
                crew_instance = sap_crew.create_crew_with_message(user_message)
            else:
                raise Exception("No crew initialized - check server logs for initialization errors")



        print("🤖 Executing CrewAI task...")
        task_output = await crew_instance.kickoff_async()

        response_content = str(task_output)
        
        # For IVA Consulta agent, ensure response is within 600 characters
        if agent_type == "iva_consulta_agent" and len(response_content) > 600:
            response_content = response_content[:597] + "..."
            print(f"⚠️  Response truncated to 600 characters for IVA Consulta agent")
        
        print(f"✅ {agent_type} response generated: {len(response_content)} characters")

        # Log successful agent interaction to LangSmith
        log_agent_interaction(
            agent_type,
            user_message,
            response_content,
            {"compliance_checked": True, "response_length": len(response_content)}
        )
        
        # Log monitoring summary if LangSmith is enabled
        if langsmith_manager.is_enabled():
            print("\n📊 Current LLM Usage Summary:")
            log_monitoring_summary()
            
        return response_content

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
        agent_type: str = data.get("agent_type", "iva_consulta_agent")  # Default to IVA Consulta
        print(f"Received message: {user_message} (agent: {agent_type})")

        # Execute the CrewAI agent call
        result: str = asyncio.run(call_crewai_agent(user_message, agent_type))

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
                    "timestamp": datetime.now().isoformat()
                }
            )

        return jsonify(
            {
                "response": result,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as exc:
        print(f"Error in chat endpoint: {exc}")
        
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


@app.route("/iva-consulta", methods=["POST"])
@limiter.limit("20 per minute")
def iva_consulta_chat():
    """IVA Consulta specific endpoint for VAT consultation with guardrails."""
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
            "server": "CrewAI RAG Agent Server with Guardrails",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health", 
                "chat": "/chat",
                "iva_consulta": "/iva-consulta"
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
    print("🏛️  IVA Consulta endpoint: /iva-consulta")
    print("🤖 CrewAI multi-agent system ready")
    print(f"📄 VAT documents: {data_path}")
    print("🎯 Default agent: IVA Consulta VAT Specialist")
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
        # Use debug=False for production
        debug_mode = is_running_locally()
        print(f"🔄 Starting Flask app on host=0.0.0.0, port={port}, debug={debug_mode}")
        app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise
