"""
Configuration Management for RagTool

Centralized configuration management that supports multiple configuration sets.
Each configuration set encapsulates all environment variables and settings
for different deployment scenarios (development, production, testing, etc.).

## Configuration Sets

Built-in configuration sets:
- **gpt-4o-mini**: OpenAI GPT-4o-mini configuration (1024 tokens)
- **google-pro**:  google Pro configuration (2048 tokens)

## Usage Examples

### Basic Usage (Backward Compatible)
```python
from agents.config import get_rag_config, get_llm_config, get_data_path
config = get_rag_config()  # Uses auto-selected configuration set
llm_config = get_llm_config()  # Gets only LLM configuration
data_path = get_data_path()
```

### Advanced Usage (New Configuration System)
```python
from agents.config import (
    get_configuration_set,
    set_configuration_set,
    create_custom_configuration_set
)

# Get current configuration set
current = get_configuration_set()
print(f"Using: {current.name} with {current.llm_model}")

# Switch to different configuration set
set_configuration_set('production')

# Create custom configuration
custom = create_custom_configuration_set(
    'my_config',
    llm_model='gpt-4o',
    llm_max_tokens=4096
)
```

### CLI Usage
```bash
# List available configuration sets
python3 -m agents.config --list-sets

# Show details for a configuration set
python3 -m agents.config --show-set production

# Set current configuration
python3 -m agents.config --set production

# Print current configuration info
python3 -m agents.config --info
```

## Environment Variables

Global environment variables (apply to all sets):
- **CONFIG_SET**: Configuration set to use (default: auto-detect)
- **API_KEY**: Generic API key that works for all providers (alternative to provider-specific keys)
- **OPENAI_API_KEY**: OpenAI-specific API key (required if using OpenAI providers)
- **GEMINI_API_KEY**: google-specific API key (required if using google providers)

Override variables (override set defaults):
- **LLM_MODEL**: LLM model name
- **EMBEDDING_MODEL**: Embedding model name
- **LLM_PROVIDER**: LLM provider (default: openai)
- **EMBEDDING_PROVIDER**: Embedding provider (default: openai)
- **LLM_MAX_TOKENS**: Maximum tokens for LLM
- **DATA_FILE_PATH**: Custom path to data file
- **CHROMA_DB_PATH**: Custom path to ChromaDB storage

## Migration from Old Configuration

The old function-based API is fully backward compatible:
- `get_rag_config()` → Now uses configuration sets internally
- `get_data_path()` → Now uses configuration sets internally
- `print_config_info()` → Enhanced with configuration set info
- All existing imports continue to work unchanged

## Auto-Selection Logic

Configuration sets are auto-selected based on:
1. `CONFIG_SET` environment variable (direct mapping to configuration set name)
2. Default → first available configuration set

### Setting Configuration via .env

Simply set the `CONFIG_SET` variable in your `.env` file:
```bash
# Use gpt-4o-mini configuration
CONFIG_SET=gpt-4o-mini

# Use google-pro configuration
CONFIG_SET=google-pro
```
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Optional dotenv support
try:
    from dotenv import load_dotenv

    # Try .env_local first (for local development), then .env
    if not load_dotenv('.env_local'):
        load_dotenv()
except ImportError:
    # dotenv not available, skip loading .env file
    pass


@dataclass
class ConfigurationSet:
    """
    A complete configuration set containing all environment variables and settings.

    Each configuration set represents a complete environment configuration
    including LLM settings, paths, and deployment-specific values.
    """

    name: str

    # LLM Configuration
    llm_model: str
    llm_provider: str
    llm_max_tokens: int

    # RAG ToolConfiguration
    rag_provider: str
    rag_model: str

    embedding_model: str
    embedding_provider: str

    chunk_size: Optional[int] = 1200
    chunk_overlap: Optional[int] = 200

    # Path Configuration
    data_filename: str = "VATBOOK1.pdf"

    data_file_path: Optional[str] = "./data/raw"
    chroma_db_path: str = "./db"

    # Environment Detection
    environment_type: str = "auto"  # auto, local, railway, testing

    # API Keys and Secrets (flexible handling)
    required_env_vars: list = field(default_factory=lambda: [])

    # LangSmith Configuration
    langsmith_enabled: bool = False
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    langsmith_endpoint: Optional[str] = None

    # Railway-specific settings
    railway_detection_vars: list = field(
        default_factory=lambda: [
            "RAILWAY_PROJECT_ID",
            "RAILWAY_SERVICE_NAME",
            "RAILWAY_ENVIRONMENT_NAME",
        ]
    )

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the configuration set.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate all required configuration parameters are set
        required_params = {
            "name": self.name,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "llm_max_tokens": self.llm_max_tokens,
        }

        for param_name, param_value in required_params.items():
            if not param_value:
                errors.append(
                    f"Required configuration parameter '{param_name}' is not set"
                )

        # Validate API keys with flexible handling
        generic_api_key = os.getenv("API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        if not generic_api_key:
            requires_openai = (
                self.llm_provider == "openai" or self.embedding_provider == "openai"
            )
            requires_gemini = (
                self.llm_provider == "google" or self.embedding_provider == "google"
            )

            missing_keys = []
            if requires_openai and not openai_api_key:
                missing_keys.append("OPENAI_API_KEY")
            if requires_gemini and not GEMINI_API_KEY:
                missing_keys.append("GEMINI_API_KEY")

            if missing_keys:
                errors.append(
                    f"Required API keys missing: {', '.join(missing_keys)}. Set these keys or use generic API_KEY."
                )

        # Check additional required environment variables
        for var in self.required_env_vars:
            if not os.getenv(var):
                errors.append(f"Required environment variable {var} is not set")

        # Check data file exists if path is specified
        data_path = self.get_data_path()
        if data_path and not os.path.exists(data_path):
            errors.append(f"Data file not found: {data_path}")

        # Validate LangSmith configuration if enabled
        if self.langsmith_enabled:
            if not self.langsmith_api_key:
                errors.append("LangSmith API key is required when LangSmith is enabled")
            if not self.langsmith_project:
                errors.append("LangSmith project name is required when LangSmith is enabled")


        return len(errors) == 0, errors

    def is_running_in_railway(self) -> bool:
        """Check if running in Railway environment."""
        if self.environment_type == "railway":
            return True
        elif self.environment_type == "local":
            return False
        elif self.environment_type == "auto":
            # Auto-detect based on Railway environment variables
            return all(os.getenv(var) for var in self.railway_detection_vars)
        else:
            return False

    def get_data_path(self) -> str:
        """Get the full path to the data file."""
        # Use custom path if specified
        if self.data_file_path:
            return self.data_file_path

        # Default paths based on environment
        if self.is_running_in_railway():
            # On Railway, try multiple possible locations
            possible_paths = [
                f"./data/raw/{self.data_filename}",
                f"./data/{self.data_filename}",
                f"/app/data/raw/{self.data_filename}",
                f"/app/data/{self.data_filename}",
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    return path

            # If none found, return the preferred path
            return f"./data/raw/{self.data_filename}"
        else:
            # Local development
            return f"./data/raw/{self.data_filename}"

    def get_storage_path(self) -> str:
        """Get the ChromaDB storage path."""
        return self.chroma_db_path

    def get_langsmith_config(self) -> Dict[str, Any]:
        """Get LangSmith configuration."""
        return {
            "enabled": self.langsmith_enabled,
            "api_key": self.langsmith_api_key,
            "project": self.langsmith_project,
            "endpoint": self.langsmith_endpoint,
        }

    def as_rag_config(self) -> Dict[str, Any]:
        """Convert to the legacy RAG configuration format."""
        return {
            "llm": {
                "provider": self.rag_provider,
                "config": {
                    "model": self.rag_model,
                },
            },
            "embedding_model": {
                "provider": self.embedding_provider,
                "config": {"model": self.embedding_model},
            },
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

    def as_llm_config(self) -> Dict[str, Any]:
        """Convert to LLM-only configuration format as plain object."""
        return {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_max_tokens": self.llm_max_tokens,
        }

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging."""
        return {
            "configuration_set": self.name,
            "is_running_in_railway": self.is_running_in_railway(),
            "is_local": not self.is_running_in_railway(),
            "environment_type": self.environment_type,
            "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "GEMINI_API_KEY_set": bool(os.getenv("GEMINI_API_KEY")),
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "data_path": self.get_data_path(),
            "storage_path": self.get_storage_path(),
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT_NAME"),
            "railway_service": os.getenv("RAILWAY_SERVICE_NAME"),
            "railway_project": os.getenv("RAILWAY_PROJECT_ID"),
        }


class ConfigurationManager:
    """
    Manager for handling multiple configuration sets.

    Provides a centralized way to manage different configuration profiles
    and automatically select the appropriate one based on environment.
    """

    def __init__(self):
        self._configuration_sets = self._initialize_default_sets()
        self._current_set = None

    def _initialize_default_sets(self) -> Dict[str, ConfigurationSet]:
        """Initialize the default configuration sets."""
        return {
            "GEMINI_2.0_FLASH": ConfigurationSet(
                name="gemini-2.0-flash",
                llm_provider="gemini",
                llm_model="gemini-2.0-flash",
                llm_max_tokens=2048,
                rag_provider="google-generativeai",
                rag_model="gemini-2.0-flash",
                embedding_provider="google-generativeai",
                embedding_model="models/embedding-001",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),

            ),
              "GEMINI_2.5_FLASH": ConfigurationSet(
                name="gemini-2.5-flash",
                llm_provider="gemini",
                llm_model="gemini-2.5-flash",
                llm_max_tokens=4096,
                rag_provider="google-generativeai",
                rag_model="gemini-2.5-flash",
                embedding_provider="google-generativeai",
                embedding_model="gemini-embedding-001",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
            ),
            "OPENAI_4o_MINI": ConfigurationSet(
                name="gpt-4o-mini",
                llm_provider="openai",
                llm_model="gpt-4o-mini",
                llm_max_tokens=1024,
                rag_provider="openai",
                rag_model="gpt-4o-mini",
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
            ),
            "GROQ_LLAMA__LIGHT_MODEL": ConfigurationSet(
                name="llama-3.1-8b-instant",
                llm_provider="groq",
                llm_model="llama-3.1-8b-instant",
                llm_max_tokens=1024,
                rag_provider="groq",
                rag_model="llama-3.1-8b-instant",
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
            ),
            "GROQ_LLAMA__MODEL": ConfigurationSet(
                name="llama-3.1-70b-versatile",
                llm_provider="groq",
                llm_model="llama-3.1-70b-versatile",
                llm_max_tokens=1024,
                rag_provider="groq",
                rag_model="llama-3.1-70b-versatile",
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
            ),
            "GROQ_MIXTRAL_MODEL": ConfigurationSet(
                name="mixtral-8x7b-32768",
                llm_provider="groq",
                llm_model="mixtral-8x7b-32768",
                llm_max_tokens=1024,
                rag_provider="groq",
                rag_model="mixtral-8x7b-32768",
                embedding_provider="openai",
                embedding_model="text-embedding-3-small",
                chunk_size=1200,
                chunk_overlap=200,
                chroma_db_path="./db",
                environment_type="auto",
                langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
                langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
                langsmith_project=os.getenv("LANGSMITH_PROJECT", "sap-rag-tool-dev"),
                langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
            ),
        }

    def add_configuration_set(self, config_set: ConfigurationSet):
        """Add a new configuration set."""
        self._configuration_sets[config_set.name] = config_set

    def get_configuration_set(self, name: str) -> Optional[ConfigurationSet]:
        """Get a specific configuration set by name."""
        return self._configuration_sets.get(name)

    def list_configuration_sets(self) -> list[str]:
        """Get a list of all available configuration set names."""
        return list(self._configuration_sets.keys())

    def load_config_set(self) -> ConfigurationSet:
        """
        Automatically select the most appropriate configuration set.

        Selection logic:
        1. Check CONFIG_SET environment variable (direct mapping to configuration set name)
        2. Default to first available configuration set
        """
        # Check for explicit configuration set selection via CONFIG_SET
        requested_set = os.getenv("CONFIG_SET")
        if requested_set:
            if requested_set in self._configuration_sets:
                print(
                    f"\n\n🎯 Using CONFIG_SET from enviromental variables, configuration set name: {requested_set}"
                )
                return self._configuration_sets[requested_set]
            else:
                available_sets = list(self._configuration_sets.keys())
                print(
                    f"⚠️  CONFIG_SET '{requested_set}' not found. Available sets: {available_sets}"
                )
                print(f"🔄 Using default configuration set: {available_sets[0]}")
                return self._configuration_sets[available_sets[0]]

        # No CONFIG_SET specified, use the first available configuration set
        default_set_name = list(self._configuration_sets.keys())[0]
        print(
            f"🏠 No CONFIG_SET specified, using default configuration: {default_set_name}"
        )
        return self._configuration_sets[default_set_name]

    def get_current_configuration_set(self) -> ConfigurationSet:
        """Get the current active configuration set."""
        if self._current_set is None:
            self._current_set = self.load_config_set()
        return self._current_set

    def set_current_configuration_set(self, name: str):
        """Set the current configuration set by name."""
        if name not in self._configuration_sets:
            raise ValueError(
                f"Configuration set '{name}' not found. Available sets: {self.list_configuration_sets()}"
            )
        self._current_set = self._configuration_sets[name]
        print(f"🔧 Configuration set changed to: {name}")


# Global configuration manager instance
_config_manager = ConfigurationManager()


# Backward compatibility functions
def get_rag_config() -> Dict[str, Any]:
    """
    Get configuration for RAG tools (CrewAI, LangChain, etc.).

    All configuration parameters must be properly set in the ConfigurationSet.
    No runtime overrides are allowed - use ConfigurationSet as single source of truth.

    Returns:
        Configuration dictionary for RAG tools

    Raises:
        ValueError: If required configuration or API keys are missing
    """

    # Get current configuration set
    current_config = _config_manager.get_current_configuration_set()

    # Validate that all required parameters are set in the configuration
    if not all(
        [
            current_config.name,
            current_config.llm_provider,
            current_config.llm_model,
            current_config.llm_max_tokens,
            current_config.embedding_provider,
            current_config.embedding_model,
            current_config.chunk_size,
            current_config.chunk_overlap,
        ]
    ):
        raise ValueError(
            "All configuration parameters (llm_provider, llm_model, embedding_provider, "
            "embedding_model, llm_max_tokens) must be set in the ConfigurationSet. "
            "No runtime overrides are allowed."
        )

    # Flexible API key validation
    _validate_api_keys(current_config)

    return current_config.as_rag_config()


def get_llm_config() -> Dict[str, Any]:
    """
    Get LLM configuration only as a plain object.

    Returns only the LLM-related configuration parameters from the ConfigurationSet
    in a flat dictionary structure with property names as keys.
    All LLM configuration parameters must be properly set in the ConfigurationSet.
    No runtime overrides are allowed - use ConfigurationSet as single source of truth.

    Returns:
        Dictionary with LLM configuration: {llm_provider, llm_model, llm_max_tokens}

    Raises:
        ValueError: If required LLM configuration or API keys are missing
    """

    # Get current configuration set
    current_config = _config_manager.get_current_configuration_set()

    # Validate that all required LLM parameters are set in the configuration
    if not all(
        [
            current_config.llm_provider,
            current_config.llm_model,
            current_config.llm_max_tokens,
        ]
    ):
        raise ValueError(
            "All LLM configuration parameters (llm_provider, llm_model, llm_max_tokens) "
            "must be set in the ConfigurationSet. No runtime overrides are allowed."
        )

    # Validate API keys for LLM provider only
    _validate_llm_api_keys(current_config)

    return current_config.as_llm_config()


def _validate_api_keys(config: ConfigurationSet):
    """
    Validate API keys with flexible handling.

    Supports either:
    1. Generic API_KEY environment variable
    2. Provider-specific keys (OPENAI_API_KEY, GEMINI_API_KEY)

    Args:
        config: The configuration set to validate against

    Raises:
        ValueError: If required API keys are missing
    """
    # Check for generic API key first
    generic_api_key = os.getenv("API_KEY")
    if generic_api_key:
        return  # Generic key is sufficient

    # Check provider-specific keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Determine which keys are required based on providers in use
    requires_openai = (
        config.llm_provider == "openai" or config.embedding_provider == "openai"
    )
    requires_gemini = (
        config.llm_provider == "gemini" or config.embedding_provider == "gemini"
    )

    missing_keys = []

    if requires_openai and not openai_api_key:
        missing_keys.append("OPENAI_API_KEY")

    if requires_gemini and not GEMINI_API_KEY:
        missing_keys.append("GEMINI_API_KEY")

    if missing_keys:
        raise ValueError(
            f"Required API keys are missing: {', '.join(missing_keys)}. "
            "Please set the required keys in your environment or .env file, "
            "or set a generic API_KEY that works for all providers."
        )


def _validate_llm_api_keys(config: ConfigurationSet):
    """
    Validate API keys for LLM provider only.

    Supports either:
    1. Generic API_KEY environment variable
    2. Provider-specific key for the LLM provider

    Args:
        config: The configuration set to validate against

    Raises:
        ValueError: If required API key for LLM provider is missing
    """
    # Check for generic API key first
    generic_api_key = os.getenv("API_KEY")
    if generic_api_key:
        return  # Generic key is sufficient

    # Check provider-specific key for LLM only
    if config.llm_provider == "openai":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for OpenAI LLM provider. "
                "Please set OPENAI_API_KEY in your environment or .env file, "
                "or set a generic API_KEY that works for all providers."
            )
    elif config.llm_provider == "gemini":
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required for google LLM provider. "
                "Please set GEMINI_API_KEY in your environment or .env file, "
                "or set a generic API_KEY that works for all providers."
            )


def get_environment_info() -> Dict[str, Any]:
    """
    Get information about the current environment.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.

    Returns:
        Dictionary with environment information
    """
    current_config = _config_manager.get_current_configuration_set()
    return current_config.get_environment_info()


def running_in_railway() -> bool:
    """
    Detect if running on Railway.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.

    Returns:
        True if running on Railway, False otherwise
    """
    current_config = _config_manager.get_current_configuration_set()
    return current_config.is_running_in_railway()


def get_data_path(filename: str = "SAP_Cloud_Platform.pdf") -> str:

    """
    Get data file path based on environment.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.

    Args:
        filename: Name of the PDF file to locate

    Returns:
        Full path to the data file
    """
    current_config = _config_manager.get_current_configuration_set()

    # Override the filename if specified
    if filename != "/home/lolou/SapRagTool/data/raw/SAP_Cloud_Platform.pdf":
        current_config.data_filename = filename
    return current_config.get_data_path()


def get_storage_path(custom_path: Optional[str] = None) -> str:
    """
    Get ChromaDB storage path based on environment.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.

    Args:
        custom_path: Override default storage path

    Returns:
        Path for ChromaDB storage
    """
    if custom_path:
        return custom_path

    current_config = _config_manager.get_current_configuration_set()
    return current_config.get_storage_path()

def get_langsmith_config() -> Dict[str, Any]:
    """
    Get LangSmith configuration.

    Returns:
        Dictionary with LangSmith configuration settings
    """
    current_config = _config_manager.get_current_configuration_set()
    return current_config.get_langsmith_config()

def print_config_info():
    """
    Print current configuration information for debugging.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.
    """
    try:
        current_config = _config_manager.get_current_configuration_set()
        env_info = current_config.get_environment_info()

        print("Printing RagTool configuaration: \n")
        print("🔧 RagTool model configuration:")
        print("-" * 60)
        print(f"Configuration Set: {current_config.name}")
        print(
            f"OpenAI API Key: {'✅ Set' if env_info['openai_api_key_set'] else '❌ Missing'}"
        )
        print(
            f"Gemini API Key: {'✅ Set' if env_info['GEMINI_API_KEY_set'] else '❌ Missing'}"
        )
        print(f"LLM Model: {current_config.llm_model}")
        print(f"LLM Provider: {current_config.llm_provider}")
        print(f"LLM Max Tokens: {current_config.llm_max_tokens}")
        print(f"Embedding Model: {current_config.embedding_model}")
        print(f"Embedding provider: {current_config.embedding_provider}")
        print(f"Chunk Size: {current_config.chunk_size}")
        print(f"Chunk Overlap: {current_config.chunk_overlap}")
        print(f"Data Path: {current_config.get_data_path()}")
        print(f"Storage Path: {current_config.get_storage_path()}")
        
        # LangSmith configuration
        langsmith_config = current_config.get_langsmith_config()
        print(f"LangSmith Enabled: {'✅ Yes' if langsmith_config['enabled'] else '❌ No'}")
        if langsmith_config['enabled']:
            print(f"LangSmith Project: {langsmith_config['project']}")
            print(f"LangSmith API Key: {'✅ Set' if langsmith_config['api_key'] else '❌ Missing'}")
            if langsmith_config['endpoint']:
                print(f"LangSmith Endpoint: {langsmith_config['endpoint']}")


        if env_info["is_running_in_railway"]:
            print(f"Railway Environment: {env_info['railway_environment']}")
            print(f"Railway Service: {env_info['railway_service']}")

        print("-" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}\n")

    print("Printing RagTool configuaration. Done.")
    print("\n" + "=" * 60)


def validate_config() -> bool:
    """
    Validate that all required configuration is available.

    BACKWARD COMPATIBILITY: This function maintains the original API
    while using the new configuration system internally.

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        current_config = _config_manager.get_current_configuration_set()
        is_valid, errors = current_config.validate()

        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")

        return is_valid

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


# New functions for direct access to configuration sets
def get_configuration_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return _config_manager


def get_configuration_set(name: Optional[str] = None) -> ConfigurationSet:
    """
    Get a specific configuration set or the current one.

    Args:
        name: Name of configuration set to get, or None for current

    Returns:
        The requested configuration set
    """
    if name:
        config_set = _config_manager.get_configuration_set(name)
        if config_set is None:
            available = _config_manager.list_configuration_sets()
            raise ValueError(
                f"Configuration set '{name}' not found. Available: {available}"
            )
        return config_set
    else:
        return _config_manager.get_current_configuration_set()


def set_configuration_set(name: str):
    """
    Set the current configuration set.

    Args:
        name: Name of configuration set to activate
    """
    _config_manager.set_current_configuration_set(name)


def list_configuration_sets() -> list[str]:
    """Get a list of all available configuration set names."""
    return _config_manager.list_configuration_sets()


def create_custom_configuration_set(name: str, **kwargs) -> ConfigurationSet:
    """
    Create a custom configuration set.

    Args:
        name: Name for the new configuration set
        **kwargs: Configuration parameters to override

    Returns:
        The created configuration set
    """
    config_set = ConfigurationSet(name=name, **kwargs)
    _config_manager.add_configuration_set(config_set)
    return config_set


if __name__ == "__main__":
    """CLI interface for configuration management."""
    import argparse

    parser = argparse.ArgumentParser(description="RagTool Configuration Management")
    parser.add_argument(
        "--info", action="store_true", help="Print current configuration"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate current configuration"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test configuration loading"
    )
    parser.add_argument(
        "--list-sets", action="store_true", help="List all available configuration sets"
    )
    parser.add_argument(
        "--set", type=str, metavar="NAME", help="Set the current configuration set"
    )
    parser.add_argument(
        "--show-set",
        type=str,
        metavar="NAME",
        help="Show details for a specific configuration set",
    )

    args = parser.parse_args()

    if args.info:
        print_config_info()
    elif args.validate:
        is_valid = validate_config()
        exit(0 if is_valid else 1)
    elif args.test:
        try:
            config = get_rag_config()
            llm_config = get_llm_config()
            print("✅ Configuration loaded successfully")
            print(f"LLM: {config['llm']['config']['model']}")
            print(f"Embedding: {config['embedding_model']['config']['model']}")
            print(f"LLM-only config: {llm_config['llm_model']}")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            exit(1)
    elif args.list_sets:
        print("📋 Available Configuration Sets:")
        for set_name in list_configuration_sets():
            current = " (current)" if get_configuration_set().name == set_name else ""
            print(f"  - {set_name}{current}")
    elif args.set:
        try:
            set_configuration_set(args.set)
            print(f"✅ Configuration set changed to: {args.set}")
        except ValueError as e:
            print(f"❌ {e}")
            exit(1)
    elif args.show_set:
        try:
            config_set = get_configuration_set(args.show_set)
            print("\n" + "Showing configuration set details:")
            print(f"🔧RagTool Configuration Details: {config_set.name}")
            print("-" * 40)
            print(f"LLM Provider: {config_set.llm_provider}")
            print(f"LLM Model: {config_set.llm_model}")
            print(f"LLM Max Tokens: {config_set.llm_max_tokens}")
            print(f"Embedding Provider: {config_set.embedding_provider}")
            print(f"Embedding Model: {config_set.embedding_model}")
            print(f"Environment Type: {config_set.environment_type}")
            print(f"Data Filename: {config_set.data_filename}")
            print(f"ChromaDB Path: {config_set.chroma_db_path}")
            print("-" * 40)
        except ValueError as e:
            print(f"❌ {e}")
            exit(1)
    else:
        print_config_info()
        print("\n" + "=" * 40)
        print("... RagTool Configuration Loader finished")
        print("=" * 40)
