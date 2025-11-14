"""
Agent Types Module

Contains custom agent-related classes for LLM and RAG tool management.
This module provides encapsulated classes for better code organization and reusability.

Classes:
    CustomLlm: Manages LLM initialization with configuration and fallback support
    CustomRagTool: Manages RAG tool initialization with PDF processing capabilities
    InsuranceCrew: CrewAI-based insurance coverage assistant with agent and task management

Version: 1.0.0
Author: CrewAI RAG Tool
"""

import os
import sys

# CrewAI imports
from crewai import LLM, Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from agents.rag.files_ragtool import (  # Import file processor for database management
    FilesRagTool,
)

# Configuration imports
from agents.utils.config import (
    get_data_path,
    get_llm_config,
    get_rag_config,
    get_storage_path,
    print_config_info,
)


class CustomLlm:
    """Custom LLM initialization and management class."""

    def __init__(self):
        """Initialize the CustomLlm class."""
        self.llm = None
        self.config = None
        self.fallback_config = {
            "llm_model": "gpt-4o-mini",
            "llm_provider": "openai",
            "llm_max_tokens": 1024,
        }

    def initialize_llm(self) -> LLM:
        """Initialize LLM with configuration and fallback handling."""
        try:
            # Initialize LLM with configuration
            print_config_info()

            self.config = get_llm_config()
            print(f"\n\nLLM configuration: {self.config}")

            llm_model = self.config["llm_model"]
            llm_provider = self.config["llm_provider"]
            llm_max_tokens = self.config["llm_max_tokens"]

            self.llm = LLM(
                model=f"{llm_provider}/{llm_model}", max_tokens=llm_max_tokens
            )
            print("✅ LLM initialized successfully with configuration")

        except Exception as e:
            print(f"❌ Configuration error: {e}")
            print("🔄 Using fallback LLM configuration...")
            self._initialize_fallback_llm()

        return self.llm

    def _initialize_fallback_llm(self):
        """Initialize LLM with fallback configuration."""
        llm_fallback_model = self.fallback_config["llm_model"]
        llm_fallback_provider = self.fallback_config["llm_provider"]
        llm_fallback_max_tokens = self.fallback_config["llm_max_tokens"]

        self.llm = LLM(
            model=f"{llm_fallback_provider}/{llm_fallback_model}",
            max_tokens=llm_fallback_max_tokens,
        )
        print("✅ LLM initialized with fallback configuration")

    def get_llm(self) -> LLM:
        """Get the initialized LLM instance."""
        if self.llm is None:
            return self.initialize_llm()
        return self.llm

    def get_config(self) -> dict:
        """Get the current LLM configuration."""
        return self.config if self.config else self.fallback_config

    def is_fallback_mode(self) -> bool:
        """Check if LLM is running in fallback mode."""
        return self.config is None

    def get_model_info(self) -> str:
        """Get formatted model information."""
        config = self.get_config()
        mode = "FALLBACK" if self.is_fallback_mode() else "CONFIG"
        return f"{config['llm_provider']}/{config['llm_model']} ({mode})"


class CustomRagTool:
    """Custom RAG tool initialization and management class."""

    def __init__(self, data_path: str = None):
        """Initialize the CustomRagTool class.

        Args:
            data_path: Optional custom data path. If None, uses default from config.
        """
        self.rag_tool = None
        self.config = None
        self.processor = None
        self.storage_path = None
        self.data_path = data_path  # Store custom data path if provided

    def initialize_rag_tool(self, data_path: str = None):
        """Initialize RAG tool with configuration and fallback handling.

        Args:
            data_path: Optional data path override. If provided, uses this instead of stored data_path or config default.
        """
        try:
            self.config = get_rag_config()
            print(f"RagTool configuration: {self.config}")

            # Configure persistent storage path using centralized config
            self.storage_path = get_storage_path()

            self.processor = FilesRagTool(self.config, self.storage_path)

            # Determine which data path to use: parameter > instance variable > config default
            actual_data_path = (
                data_path
                if data_path is not None
                else (self.data_path if self.data_path is not None else get_data_path())
            )

            # If we're switching data paths, reset the processor to force reprocessing
            if actual_data_path != self.data_path and self.data_path is not None:
                print(
                    f"🔄 Switching data path from {self.data_path} to {actual_data_path}"
                )
                # Reset processor to force new database
                if self.processor:
                    self.processor.rag_tool = None

            # Update stored data path
            if actual_data_path is not None:
                self.data_path = actual_data_path

            # Try to load existing ChromaDB first
            raw_rag_tool = self.processor.get_rag_tool()

            if raw_rag_tool is None:
                # No existing database, process PDFs for the first time
                print(
                    "🔄 No existing RagTool found. Processing PDFs for the first time..."
                )

                if os.path.exists(self.data_path):
                    # Check if data_path is a directory or a file
                    if os.path.isdir(self.data_path):
                        # It's a directory, find all supported files
                        supported_files = []
                        for filename in os.listdir(self.data_path):
                            file_path = os.path.join(self.data_path, filename)
                            if os.path.isfile(
                                file_path
                            ) and self.processor._is_supported_file(file_path):
                                supported_files.append(file_path)

                        if supported_files:
                            print(
                                f"📄 Will process: {self.data_path} (type: directory)"
                            )
                            print(f"🔄 Processing {len(supported_files)} files...")
                            success = (
                                self.processor.initialize_ragtool_and_process_files(
                                    supported_files
                                )
                            )
                        else:
                            print(f"⚠️  No supported files found in {self.data_path}")
                            success = False
                    else:
                        # It's a single file
                        print(f"📄 Will process: {self.data_path}")
                        print("🔄 Processing 1 files...")
                        success = self.processor.initialize_ragtool_and_process_files(
                            [self.data_path]
                        )

                    if success:
                        raw_rag_tool = self.processor.rag_tool
                        print(f"✅ Successfully processed and loaded: {self.data_path}")
                    else:
                        print("❌ Failed to process files")
                        raw_rag_tool = None
                else:
                    print(f"⚠️  File or directory not found: {self.data_path}")
                    raw_rag_tool = None
            else:
                print(
                    "✅ Successfully loaded existing RagTool - no reprocessing needed"
                )

            # Wrap the RAG tool for CrewAI compatibility
            if raw_rag_tool is not None:
                from agents.rag.rag_wrapper import create_rag_wrapper

                self.rag_tool = create_rag_wrapper(raw_rag_tool)
                print("🔧 RAG tool wrapped for CrewAI compatibility")
            else:
                self.rag_tool = None

        except Exception as e:
            print(f"⚠️  Warning: Could not initialize RAGTool: {e}")
            print("🔄 Agent will continue without RAG capabilities")
            self.rag_tool = None

        return self.rag_tool

    def get_rag_tool(self):
        """Get the initialized RAG tool instance."""
        if self.rag_tool is None:
            return self.initialize_rag_tool()
        return self.rag_tool

    def is_available(self) -> bool:
        """Check if RAG tool is available and functional."""
        return self.rag_tool is not None

    def get_config(self) -> dict:
        """Get the current RAG configuration."""
        return self.config if self.config else {}

    def get_data_info(self) -> str:
        """Get formatted data information."""
        if self.data_path:
            return f"Data: {self.data_path}"
        return "No data path configured"

    def get_status_info(self) -> str:
        """Get formatted status information."""
        status = "ENABLED" if self.is_available() else "DISABLED"
        return f"RAG Tool: {status}"

    def refresh_rag_tool(self, data_path: str = None):
        """Force refresh/re-initialization of the RAG tool.

        Args:
            data_path: Optional data path to use for reinitialization.
        """
        print("🔄 Refreshing RAG tool...")
        self.rag_tool = None
        if self.processor:
            self.processor.rag_tool = None
        # If data_path provided, update stored data_path
        if data_path is not None:
            self.data_path = data_path
        return self.initialize_rag_tool(data_path=data_path)

    def get_detailed_status(self) -> dict:
        """Get detailed status information."""
        return {
            "available": self.is_available(),
            "config": self.get_config(),
            "storage_path": self.storage_path,
            "data_path": self.data_path,
            "processor_loaded": self.processor is not None,
        }


@CrewBase
class SapCrew:
    """SAP Consulting Crew"""

    agents_config = "sap_agents.yaml"
    tasks_config = "sap_tasks.yaml"

    def __init__(
        self, custom_llm_instance: CustomLlm, custom_rag_tool_instance: CustomRagTool
    ):
        """Initialize SapCrew with CustomLlm and CustomRagTool instances."""
        self.custom_llm = custom_llm_instance
        self.custom_rag_tool = custom_rag_tool_instance

        # Check if YAML files exist
        # current_dir = os.path.dirname(__file__)
                
        current_dir = os.path(__file__).resolve().parent

        agents_config_path, agents_used_fallback = resolve_config_path(
            "sap_agents.yaml", "agents.yaml"
        )
        tasks_config_path, tasks_used_fallback = resolve_config_path(
            "sap_tasks.yaml", "tasks.yaml"
        )
        self.original_agents_config_path = str(agents_config_path)
        self.original_tasks_config_path = str(tasks_config_path)


        agents_yaml_path = os.path.join(current_dir, "agents.yaml")
        tasks_yaml_path = os.path.join(current_dir, "tasks.yaml")

        print(f"🔍 Checking YAML files:")
        print(
            f"   - Agents YAML: {agents_yaml_path} (exists: {os.path.exists(agents_yaml_path)})"
        )
        print(
            f"   - Tasks YAML: {tasks_yaml_path} (exists: {os.path.exists(tasks_yaml_path)})"
        )

        print("✅ SapCrew initialized successfully")



    @agent
    def senior_sap_consultant(self) -> Agent:
        """Create the senior SAP consultant agent with proper configuration."""
        try:
            print("🔍 Creating senior SAP consultant agent...")

            # Determine tools to use based on RAG availability
            tools = []
            if self.custom_rag_tool.is_available():
                tools.append(self.custom_rag_tool.get_rag_tool())
                print("✅ RAG tool available - SAP agent will use RAG capabilities")
            else:
                print(
                    "⚠️  No RAG tool available - SAP agent will use base knowledge only"
                )

            print(f"🔍 Agent config: {self.agents_config}")
            print(f"🔍 LLM: {self.custom_llm.get_llm()}")
            print(f"🔍 Tools: {tools}")

            return Agent(
                config=self.agents_config["senior_sap_consultant"],
                verbose=is_running_locally(),
                allow_delegation=False,
                llm=self.custom_llm.get_llm(),
                tools=tools,
                max_iterations=10,
                max_retry_limit=5,
            )
        except Exception as e:
            print(f"❌ Error creating senior SAP consultant: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            # Fallback agent creation
            return Agent(
                role="Senior SAP Consultant",
                goal="Provide SAP consulting services to the user",
                backstory="You are an expert SAP consultant designed to assist with SAP consulting queries.",
                verbose=False,
                allow_delegation=False,
                llm=self.custom_llm.get_llm(),
                tools=[],
                max_iterations=5,
                max_retry_limit=2,
            )

    @task
    def sap_consultation_task(self, description: str = None) -> Task:
        """Create the SAP consultation task."""
        try:
            print(f"🔍 Creating SAP consultation task with description: {description}")
            return Task(
                description=description,
                expected_output="A comprehensive response to the user's question about SAP consulting, including specific details about SAP consulting, limitations, and any relevant SAP information. The response should be clear, accurate, and helpful to the user.",
                agent=self.senior_sap_consultant(),
            )
        except Exception as e:
            print(f"❌ Error creating SAP consultation task: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            raise e

    @crew
    def crew(self) -> Crew:
        """Create the SAP crew."""
        return Crew(
            agents=[self.senior_sap_consultant()],
            tasks=[self.sap_consultation_task()],
            verbose=is_running_locally(),
        )

    def create_crew_with_message(
        self, user_message: str, context_country: str = None
    ) -> Crew:
        """Create the SAP crew with a custom user message.

        Args:
            user_message: The user's question/message
            context_country: Optional country context to provide jurisdictional context
        """
        try:
            # Build task description with optional country context
            task_description = user_message
            if context_country:
                task_description = f"Context: The user is asking in the context of {context_country}. {user_message}"
                print(
                    f"🔍 Creating SAP crew with message and country context: {context_country}"
                )
            else:
                print(f"🔍 Creating SAP crew with message: {user_message}")

            return Crew(
                agents=[self.senior_sap_consultant()],
                tasks=[self.sap_consultation_task(description=task_description)],
                verbose=is_running_locally(),
            )
        except Exception as e:
            print(f"❌ Error creating SAP crew with message: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            raise e
        
    def resolve_config_path(
            self, preferred_name: str, fallback_name: str
        ) -> tuple[os.path, bool]:
            preferred_path = (self.current_dir / preferred_name).resolve()
            if preferred_path.exists():
                return preferred_path, False
            fallback_path = (self.current_dir / fallback_name).resolve()
            if fallback_path.exists():
                return fallback_path, True
            return preferred_path, False


@CrewBase
class IVAConsultaCrew:
    """IVA Consulta VAT Specialist Crew"""

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    def __init__(
        self, custom_llm_instance: CustomLlm, custom_rag_tool_instance: CustomRagTool
    ):
        """Initialize IVAConsultaCrew with CustomLlm and CustomRagTool instances."""
        self.custom_llm = custom_llm_instance
        self.custom_rag_tool = custom_rag_tool_instance

        # Load agents and tasks from YAML files
        from pathlib import Path

        import yaml

        agents_dir = Path(__file__).parent
        try:
            with open(agents_dir / "agents.yaml", "r", encoding="utf-8") as file:
                self.agents_config = yaml.safe_load(file)
            with open(agents_dir / "tasks.yaml", "r", encoding="utf-8") as file:
                self.tasks_config = yaml.safe_load(file)
            print("✅ IVA Consulta crew loaded agents and tasks from YAML")
        except Exception as e:
            print(f"⚠️  Warning: Could not load YAML configs: {e}")
            self.agents_config = {}
            self.tasks_config = {}

    @agent
    def iva_consulta_agent(self) -> Agent:
        """Create the IVA Consulta agent with proper configuration."""
        try:
            # Determine tools to use based on RAG availability
            tools = []
            if self.custom_rag_tool.is_available():
                tools.append(self.custom_rag_tool.get_rag_tool())
                print(
                    "✅ RAG tool available - IVA Consulta agent will use RAG capabilities"
                )
            else:
                print(
                    "⚠️  No RAG tool available - IVA Consulta agent will use base knowledge only"
                )

            return Agent(
                config=self.agents_config["iva_consulta_agent"],
                verbose=is_running_locally(),
                allow_delegation=False,
                llm=self.custom_llm.get_llm(),
                tools=tools,
                max_iterations=10,
                max_retry_limit=5,
            )
        except Exception as e:
            print(f"❌ Error creating IVA Consulta agent: {e}")
            # Fallback agent creation
            return Agent(
                role="IVA Consulta VAT Specialist",
                goal="Provide expert VAT and indirect taxation consultation services for Spanish and international companies",
                backstory="You are a specialized VAT consultant from IVA Consulta, expert in Spanish and European indirect taxation.",
                verbose=False,
                allow_delegation=False,
                llm=self.custom_llm.get_llm(),
                tools=[],
                max_iterations=5,
                max_retry_limit=2,
            )

    @task
    def vat_consultation_task(self, description: str = None) -> Task:
        """Create the VAT consultation task."""
        if description:
            # Create task with custom description for dynamic user messages
            return Task(
                description=description,
                expected_output="A concise and professional response about VAT and indirect taxation. The response should include specific VAT rules, compliance requirements, or procedures relevant to the user's question. If referencing another country, clearly specify the jurisdiction. The response should be practical, accurate, and directly helpful for business decision-making.",
                agent=self.iva_consulta_agent(),
            )
        else:
            # Use configuration from YAML
            return Task(
                config=self.tasks_config["vat_consultation_task"],
                agent=self.iva_consulta_agent(),
            )

    @crew
    def crew(self) -> Crew:
        """Create the IVA Consulta crew."""
        return Crew(
            agents=[self.iva_consulta_agent()],
            tasks=[self.vat_consultation_task()],
            verbose=is_running_locally(),
        )

    def create_crew_with_message(
        self, user_message: str, context_country: str = None
    ) -> Crew:
        """Create the IVA Consulta crew with a custom user message.

        Args:
            user_message: The user's question/message
            context_country: Optional country context to provide jurisdictional context for VAT queries
        """
        # Build task description with optional country context
        task_description = user_message
        if context_country:
            task_description = f"Context: The user is asking about VAT regulations in the context of {context_country}. {user_message}"
            print(
                f"🔍 Creating IVA Consulta crew with message and country context: {context_country}"
            )
        else:
            print(f"🔍 Creating IVA Consulta crew with message: {user_message}")

        return Crew(
            agents=[self.iva_consulta_agent()],
            tasks=[self.vat_consultation_task(description=task_description)],
            verbose=is_running_locally(),
        )

    @agent
    def senior_coverage_assistant(self) -> Agent:
        """Create the senior coverage assistant agent (for compatibility)."""
        return Agent(
            role="Senior Insurance Coverage Assistant",
            goal="Determine whether something is covered or not under insurance policies",
            backstory="You are an expert insurance agent designed to assist with coverage queries.",
            verbose=is_running_locally(),
            allow_delegation=False,
            llm=self.custom_llm.get_llm(),
            tools=[],
            max_iterations=5,
            max_retry_limit=2,
        )

    @agent
    def senior_sap_consultant(self) -> Agent:
        """Create the senior SAP consultant agent (for compatibility)."""
        return Agent(
            role="Senior SAP Consultant",
            goal="Provide SAP consulting services to the user.",
            backstory="You are an expert SAP consultant designed to assist with SAP consulting queries.",
            verbose=is_running_locally(),
            allow_delegation=False,
            llm=self.custom_llm.get_llm(),
            tools=[],
            max_iterations=5,
            max_retry_limit=2,
        )

    @task
    def coverage_analysis_task(self, description: str = None) -> Task:
        """Create the coverage analysis task (for compatibility)."""
        return Task(
            description=description or "Analyze insurance coverage question",
            expected_output="A comprehensive response about insurance coverage",
            agent=self.senior_coverage_assistant(),
        )

    @task
    def sap_consultation_task(self, description: str = None) -> Task:
        """Create the SAP consultation task (for compatibility)."""
        return Task(
            description=description or "Provide SAP consulting services",
            expected_output="A comprehensive response about SAP consulting",
            agent=self.senior_sap_consultant(),
        )


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
        return True

    # Check if the environment variables are not just empty strings
    if railway_env.strip() == "" or railway_service.strip() == "":
        return True

    # If Railway-specific vars are present and not empty, we're on Railway
    return False
