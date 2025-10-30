#!/usr/bin/env python3
"""
Test script for IVA Consulta agent with guardrails
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Test the guardrails server functionality
async def test_guardrails_iva_consulta():
    """Test the IVA Consulta agent with guardrails."""
    print("🧪 Testing IVA Consulta Agent with Guardrails")
    print("=" * 60)
    
    # Import the call_crewai_agent function from the guardrails server
    try:
        from agents.crewai.crew_agent_server_with_guard_rails import call_crewai_agent
        print("✅ Guardrails server functions imported successfully")
    except Exception as e:
        print(f"❌ Error importing guardrails server: {e}")
        return
    
    # Test questions
    test_questions = [
        "¿Cuál es el IVA en España para servicios digitales?",
        "¿Qué documentos necesito para la declaración de IVA?",
        "¿Cómo funciona el IVA intracomunitario?",
        "¿Cuáles son las obligaciones de IVA para empresas extranjeras en España?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 50)
        
        try:
            # Test with default agent (should be iva_consulta_agent)
            response = await call_crewai_agent(question)
            print(f"✅ Default Response ({len(response)} chars): {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_guardrails_iva_consulta())
