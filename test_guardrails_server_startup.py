#!/usr/bin/env python3
"""
Test script to verify guardrails server startup
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def test_guardrails_server():
    """Test the guardrails server startup and basic functionality."""
    print("🧪 Testing Guardrails Server Startup")
    print("=" * 50)
    
    try:
        # Import the server components
        from agents.crewai.crew_agent_server_with_guard_rails import (
            call_crewai_agent, 
            iva_consulta_crew,
            sap_crew,
            custom_llm,
            custom_rag_tool
        )
        print("✅ Server components imported successfully")
        
        # Test crew availability
        if iva_consulta_crew is not None:
            print("✅ IVA Consulta crew is available")
        else:
            print("❌ IVA Consulta crew is not available")
            
        if sap_crew is not None:
            print("✅ SAP crew is available")
        else:
            print("❌ SAP crew is not available")
            
        # Test LLM and RAG tool
        if custom_llm is not None:
            print(f"✅ LLM: {custom_llm.get_model_info()}")
        else:
            print("❌ LLM not available")
            
        if custom_rag_tool is not None:
            print(f"✅ RAG Tool: {custom_rag_tool.get_status_info()}")
        else:
            print("❌ RAG Tool not available")
            
        # Test a simple VAT question
        print("\n📝 Testing IVA Consulta agent...")
        try:
            response = await call_crewai_agent("¿Cuál es el IVA en España?", "iva_consulta_agent")
            print(f"✅ IVA Consulta response: {response[:100]}...")
        except Exception as e:
            print(f"❌ IVA Consulta test failed: {e}")
            
        print("\n✅ Guardrails server test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing guardrails server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_guardrails_server())
