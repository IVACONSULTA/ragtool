#!/usr/bin/env python3
"""
Test RAG Tool Wrapper

This script tests the RAG tool wrapper to debug the tool calling issue.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def test_rag_tool():
    """Test RAG tool wrapper."""
    print("🧪 Testing RAG Tool Wrapper")
    print("=" * 40)

    try:
        # Import required modules
        print("📦 Importing modules...")
        from agents.crewai.crew_entities import CustomLlm, CustomRagTool
        from agents.rag.rag_wrapper import create_rag_wrapper

        print("✅ Modules imported successfully")

        # Initialize CustomLlm
        print("\n🤖 Initializing CustomLlm...")
        custom_llm = CustomLlm()
        llm = custom_llm.initialize_llm()
        print(f"✅ CustomLlm initialized: {custom_llm.get_model_info()}")

        # Initialize CustomRagTool
        print("\n🔧 Initializing CustomRagTool...")
        custom_rag_tool = CustomRagTool()
        rag_tool = custom_rag_tool.initialize_rag_tool()
        print(f"✅ CustomRagTool initialized: {custom_rag_tool.get_status_info()}")

        # Test RAG tool wrapper
        print("\n🔧 Testing RAG tool wrapper...")
        if custom_rag_tool.is_available():
            wrapped_tool = custom_rag_tool.get_rag_tool()
            print(f"✅ RAG tool wrapper created: {wrapped_tool}")
            print(f"   - Name: {wrapped_tool.name}")
            print(f"   - Description: {wrapped_tool.description}")
            print(f"   - Args schema: {wrapped_tool.args_schema}")

            # Test direct call
            print("\n🔍 Testing direct RAG tool call...")
            try:
                result = wrapped_tool("SAP consulting")
                print(f"✅ Direct call successful: {result[:100]}...")
            except Exception as e:
                print(f"❌ Direct call failed: {e}")

            # Test with different input formats
            print("\n🔍 Testing different input formats...")
            test_inputs = [
                "SAP consulting",
                {"query": "SAP consulting"},
                {"description": "SAP consulting"},
                {"action": "none", "query": "SAP consulting"},
            ]

            for i, test_input in enumerate(test_inputs):
                try:
                    print(f"   Test {i+1}: {test_input}")
                    result = wrapped_tool(test_input)
                    print(f"   ✅ Success: {result[:50]}...")
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
        else:
            print("❌ RAG tool not available")
            return False

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")

        # Print more debugging info
        import traceback

        print(f"\n📋 Full traceback:")
        traceback.print_exc()

        return False


if __name__ == "__main__":
    success = test_rag_tool()
    sys.exit(0 if success else 1)
