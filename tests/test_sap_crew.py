#!/usr/bin/env python3
"""
Test SAP Crew Initialization

This script tests the SAP Crew initialization to help debug issues.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_sap_crew():
    """Test SAP Crew initialization."""
    print("🧪 Testing SAP Crew Initialization")
    print("=" * 40)
    
    try:
        # Import required modules
        print("📦 Importing modules...")
        from agents.crewai.crew_entities import CustomLlm, CustomRagTool, SapCrew
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
        
        # Initialize SapCrew
        print("\n🚀 Initializing SapCrew...")
        sap_crew = SapCrew(custom_llm, custom_rag_tool)
        print("✅ SapCrew initialized successfully")
        
        # Test creating a crew with message
        print("\n💬 Testing crew creation with message...")
        test_message = "Hello, I need help with SAP"
        crew_instance = sap_crew.create_crew_with_message(test_message)
        print("✅ Crew created successfully")
        
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
    success = test_sap_crew()
    sys.exit(0 if success else 1)
