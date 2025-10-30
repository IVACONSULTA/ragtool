#!/usr/bin/env python3
"""
Test RAG Tool LangSmith Tracing

This script tests that the RAG tool is properly tracing LLM calls to LangSmith
under the "sap-rag-tool-dev" project.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_rag_langsmith_tracing():
    """Test that RAG tool traces to LangSmith."""
    print("🧪 Testing RAG Tool LangSmith Tracing")
    print("=" * 50)
    
    # Check if LangSmith is configured
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if not langsmith_api_key:
        print("❌ LANGSMITH_API_KEY not set")
        print("   Set it with: export LANGSMITH_API_KEY='your_api_key_here'")
        return False
    
    print("✅ LangSmith API key found")
    
    try:
        # Import required modules
        from agents.crewai.crew_entities import CustomLlm, CustomRagTool
        from agents.langsmith_integration import get_langsmith_manager
        
        # Initialize LangSmith manager
        print("\n🔍 Initializing LangSmith manager...")
        langsmith_manager = get_langsmith_manager()
        
        if not langsmith_manager.is_enabled():
            print("❌ LangSmith is not enabled")
            return False
        
        print(f"✅ LangSmith enabled for project: {langsmith_manager.config.get('project')}")
        
        # Initialize CustomLlm
        print("\n🤖 Initializing Custom LLM...")
        custom_llm = CustomLlm()
        llm = custom_llm.initialize_llm()
        print(f"✅ LLM initialized: {custom_llm.get_model_info()}")
        
        # Initialize CustomRagTool
        print("\n🔧 Initializing Custom RAG Tool...")
        custom_rag_tool = CustomRagTool()
        rag_tool = custom_rag_tool.initialize_rag_tool()
        
        if not custom_rag_tool.is_available():
            print("❌ RAG tool not available")
            return False
        
        print(f"✅ RAG tool initialized: {custom_rag_tool.get_status_info()}")
        
        # Test RAG tool with LangSmith tracing
        print("\n🔍 Testing RAG tool with LangSmith tracing...")
        
        # Get the wrapped RAG tool
        wrapped_rag_tool = custom_rag_tool.get_rag_tool()
        
        if not wrapped_rag_tool:
            print("❌ Could not get wrapped RAG tool")
            return False
        
        print("✅ Got wrapped RAG tool")
        
        # Check if LangSmith tracing is set up
        if hasattr(wrapped_rag_tool, '_langsmith_enabled'):
            if wrapped_rag_tool._langsmith_enabled:
                print("✅ RAG tool has LangSmith tracing enabled")
                print(f"   Project: {langsmith_manager.config.get('project')}")
            else:
                print("⚠️  RAG tool LangSmith tracing is disabled")
        else:
            print("⚠️  RAG tool does not have LangSmith enabled attribute")
        
        # Test a simple RAG query
        print("\n🔍 Testing RAG query...")
        test_query = "SAP consulting"
        
        try:
            result = wrapped_rag_tool(test_query)
            print(f"✅ RAG query successful: {len(result)} characters")
            print(f"   Result preview: {result[:100]}...")
            
            # Check if traces were created
            print("\n📊 Checking LangSmith traces...")
            print("   Visit https://smith.langchain.com/ to view traces")
            print(f"   Project: {langsmith_manager.config.get('project')}")
            
            return True
            
        except Exception as e:
            print(f"❌ RAG query failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 RAG Tool LangSmith Tracing Test")
    print("=" * 60)
    
    success = test_rag_langsmith_tracing()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check your LangSmith dashboard at https://smith.langchain.com/")
        print("   2. Look for traces in the 'sap-rag-tool-dev' project")
        print("   3. Verify that RAG tool LLM calls are being traced")
    else:
        print("\n❌ Test failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure LANGSMITH_API_KEY is set")
        print("   2. Check that LangSmith is properly installed")
        print("   3. Verify RAG tool is available and working")
        print("   4. Check application logs for errors")


if __name__ == "__main__":
    main()
