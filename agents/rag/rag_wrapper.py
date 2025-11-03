"""
RAG Tool Wrapper for CrewAI Compatibility

This wrapper ensures proper input validation and compatibility with CrewAI agents.
It addresses validation errors that can occur with newer CrewAI versions.
"""

from typing import Any, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, field_validator, model_validator


class RagToolInputSchema(BaseModel):
    """Input schema for RAG tool."""

    query: str = Field(description="The search query for the knowledge base")

    @model_validator(mode="before")
    @classmethod
    def validate_input(cls, data):
        """
        Handle various input formats that CrewAI might send.
        CrewAI sometimes sends dict objects instead of strings.
        """

        if isinstance(data, dict):
            # If it's a dict, extract the query from description or other fields
            if "description" in data:
                return {"query": str(data["description"])}
            elif "query" in data:
                return {"query": str(data["query"])}
            else:
                # Try to find any string value
                string_values = [val for val in data.values() if isinstance(val, str)]
                if string_values:
                    return {"query": string_values[0]}
                # If no string values, convert the first value to string
                elif data:
                    first_value = next(iter(data.values()))
                    return {"query": str(first_value)}
        elif isinstance(data, str):
            return {"query": data}
        else:
            return {"query": str(data)}

    @field_validator("query", mode="before")
    @classmethod
    def validate_query(cls, v):
        """
        Additional validation for the query field.
        """
        if isinstance(v, str):
            return v.strip()
        return str(v).strip()


class RagToolWrapper(BaseTool):
    """
    Wrapper for RagTool that ensures proper input validation.

    This wrapper addresses issues with CrewAI tool validation by providing
    proper input handling and inheriting from BaseTool.
    """

    name: str = "knowledge_base"
    description: str = (
        "Search for information in the knowledge base. Use this tool to find relevant information about SAP consulting, insurance coverage, waiting periods, and policy details. "
        "Call with: knowledge_base(query='your search query')"
    )
    args_schema: Type[BaseModel] = RagToolInputSchema

    def __call__(self, *args, **kwargs):
        """Override call to handle input parsing better."""
        print(f"🔍 RagToolWrapper.__call__ received args: {args}, kwargs: {kwargs}")

        # Handle different input formats
        if args:
            if len(args) == 1:
                arg = args[0]
                if isinstance(arg, str):
                    # Direct string input
                    return self._run(arg)
                elif isinstance(arg, dict):
                    # Dictionary input - extract query
                    # Handle various dict formats that CrewAI might send
                    if "query" in arg:
                        return self._run(str(arg["query"]))
                    elif "description" in arg:
                        return self._run(str(arg["description"]))
                    elif "action" in arg and "query" in arg:
                        # Handle action-based calls - ignore action, use query
                        print(
                            f"🔍 Ignoring action '{arg.get('action')}', using query: {arg.get('query')}"
                        )
                        return self._run(str(arg["query"]))
                    else:
                        # Try to find any string value
                        string_values = [v for v in arg.values() if isinstance(v, str)]
                        if string_values:
                            return self._run(string_values[0])
                        # If no string values, convert the first value to string
                        elif arg:
                            first_value = next(iter(arg.values()))
                            return self._run(str(first_value))
                else:
                    # Convert any other type to string
                    return self._run(str(arg))

        if "query" in kwargs:
            return self._run(str(kwargs["query"]))

        # Fall back to parent implementation with error handling
        try:
            return super().__call__(*args, **kwargs)
        except Exception as e:
            print(f"❌ RagToolWrapper fallback failed: {e}")
            # As a last resort, try to extract any meaningful input
            if args:
                return self._run(str(args[0]))
            elif kwargs:
                first_val = next(iter(kwargs.values()))
                return self._run(str(first_val))
            else:
                return "Please provide a valid search query."

    def __init__(self, rag_tool: Any):
        """
        Initialize wrapper with the actual RagTool instance.

        Args:
            rag_tool: The CrewAI RagTool instance
        """
        super().__init__()
        self._rag_tool = rag_tool
        self._langsmith_enabled = False
        self._setup_langsmith_tracing()

    def _setup_langsmith_tracing(self):
        """Set up LangSmith tracing for the RAG tool's internal LLM calls."""
        try:
            # Import LangSmith integration
            from agents.langsmith_integration import get_langsmith_manager

            langsmith_manager = get_langsmith_manager()

            if langsmith_manager.is_enabled():
                print("🔍 Setting up LangSmith tracing for RAG tool...")

                # Set environment variables for automatic tracing
                import os

                os.environ["LANGCHAIN_TRACING_V2"] = "true"

                # Get config values
                endpoint = langsmith_manager.config.get("endpoint")
                api_key = langsmith_manager.config.get("api_key")
                project = langsmith_manager.config.get("project", "sap-rag-tool-dev")

                if endpoint:
                    os.environ["LANGCHAIN_ENDPOINT"] = endpoint
                else:
                    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

                if api_key:
                    os.environ["LANGCHAIN_API_KEY"] = api_key

                os.environ["LANGCHAIN_PROJECT"] = project

                self._langsmith_enabled = True
                print(f"✅ LangSmith tracing enabled for RAG tool (project: {project})")
            else:
                print("⚠️  LangSmith tracing disabled for RAG tool")
                self._langsmith_enabled = False

        except Exception as e:
            print(f"⚠️  Could not set up LangSmith tracing for RAG tool: {e}")
            self._langsmith_enabled = False

    def _run(self, query: (str, dict), **kwargs) -> str:
        """
        Execute the RAG search with proper input validation and LangSmith tracing.

        Args:
            query: Search query string
            **kwargs: Additional keyword arguments

        Returns:
            Search results from the knowledge base
        """
        try:
            # Debug logging
            print(f"🔍 RAG Tool received query: {query} (type: {type(query)})")
            if kwargs:
                print(f"🔍 RAG Tool received kwargs: {kwargs}")

            # Ensure query is a string
            if not isinstance(query, str):
                if isinstance(query, dict):
                    if "description" in query:
                        query = str(query["description"])
                    elif "query" in query:
                        query = str(query["query"])
                    else:
                        # Try to get the first string value
                        string_values = [
                            v for v in query.values() if isinstance(v, str)
                        ]
                        query = string_values[0] if string_values else str(query)
                else:
                    query = str(query)

            # Clean and validate query
            query = query.strip()
            if not query:
                return "Please provide a valid search query."

            print(f"🔍 Searching knowledge base for: {query}")

            # Log RAG operation to LangSmith if available
            if self._langsmith_enabled:
                try:
                    from agents.langsmith_integration import log_rag_operation

                    log_rag_operation("search", query, "Starting RAG search...")
                except Exception as e:
                    print(f"⚠️  Could not log RAG operation to LangSmith: {e}")

            # Call the actual RagTool
            result = self._rag_tool._run(query)

            # Ensure result is a string
            if not isinstance(result, str):
                result = str(result)

            print(f"✅ Found knowledge base results ({len(result)} characters)")

            # Log successful RAG operation to LangSmith if available
            if self._langsmith_enabled:
                try:
                    from agents.langsmith_integration import log_rag_operation

                    log_rag_operation(
                        "search",
                        query,
                        result[:500] + "..." if len(result) > 500 else result,
                    )
                except Exception as e:
                    print(f"⚠️  Could not log RAG result to LangSmith: {e}")
            return result

        except Exception as e:
            error_msg = f"Error searching knowledge base: {str(e)}"
            print(f"❌ RAG Tool Error: {error_msg}")

            # Log error to LangSmith if available
            if self._langsmith_enabled:
                try:
                    from agents.langsmith_integration import log_error

                    log_error(e, "rag_tool_search", {"query": str(query)})
                except Exception as log_e:
                    print(f"⚠️  Could not log RAG error to LangSmith: {log_e}")
            return error_msg

    async def _arun(self, query: str, **kwargs) -> str:
        """
        Async version of _run (required by BaseTool).

        Args:
            query: Search query string
            **kwargs: Additional keyword arguments

        Returns:
            Search results from the knowledge base
        """
        # For now, just call the sync version
        # The sync version already includes LangSmith tracing

        return self._run(query, **kwargs)


def create_rag_wrapper(rag_tool: Any) -> RagToolWrapper:
    """
    Create a wrapped RAG tool for CrewAI compatibility.

    Args:
        rag_tool: The original RagTool instance

    Returns:
        Wrapped RAG tool with proper validation
    """
    return RagToolWrapper(rag_tool)
