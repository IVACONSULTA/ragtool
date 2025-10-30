#!/usr/bin/env python3
"""
Test script for default IVA Consulta agent
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.crewai.crew_agent_server import call_crewai_agent

async def test_default_iva_consulta():
    """Test the default IVA Consulta agent."""
    print("🧪 Testing Default IVA Consulta Agent")
    print("=" * 50)
    
    # Test questions
    test_questions = [
        "¿Cuál es el IVA en España para servicios digitales?",
        "¿Qué documentos necesito para la declaración de IVA?",
        "¿Cómo funciona el IVA intracomunitario?",
        "¿Cuáles son las obligaciones de IVA para empresas extranjeras en España?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 40)
        
        try:
            # Test with default agent (should be iva_consulta_agent)
            response = await call_crewai_agent(question)
            print(f"✅ Default Response ({len(response)} chars): {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_default_iva_consulta())
