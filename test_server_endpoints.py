#!/usr/bin/env python3
"""
Test script for server endpoints
"""

import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path

def test_server_endpoints():
    """Test the server endpoints."""
    print("🧪 Testing Server Endpoints")
    print("=" * 50)
    
    # Start the server in the background
    print("🚀 Starting server...")
    server_process = subprocess.Popen([
        sys.executable, 
        "agents/crewai/crew_agent_server_with_guard_rails.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(10)
    
    try:
        # Test health endpoint
        print("\n📋 Testing /health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
            print(f"   - Environment: {health_data.get('environment', 'unknown')}")
            print(f"   - RAG enabled: {health_data.get('rag_enabled', False)}")
            print(f"   - LLM model: {health_data.get('llm_model', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
        # Test index endpoint
        print("\n📋 Testing / endpoint...")
        response = requests.get("http://localhost:8001/", timeout=10)
        if response.status_code == 200:
            index_data = response.json()
            print(f"✅ Index endpoint passed")
            print(f"   - Server: {index_data.get('server', 'unknown')}")
            print(f"   - Default agent: {index_data.get('default_agent', 'unknown')}")
            print(f"   - Guardrails: {index_data.get('guardrails', 'unknown')}")
        else:
            print(f"❌ Index endpoint failed: {response.status_code}")
            
        # Test IVA Consulta endpoint
        print("\n📋 Testing /iva-consulta endpoint...")
        test_data = {
            "message": "¿Cuál es el IVA en España?"
        }
        response = requests.post(
            "http://localhost:8001/iva-consulta", 
            json=test_data, 
            timeout=30
        )
        if response.status_code == 200:
            iva_data = response.json()
            print(f"✅ IVA Consulta endpoint passed")
            print(f"   - Response length: {len(iva_data.get('response', ''))}")
            print(f"   - Agent type: {iva_data.get('agent_type', 'unknown')}")
            print(f"   - Source: {iva_data.get('source', 'unknown')}")
            print(f"   - Response preview: {iva_data.get('response', '')[:100]}...")
        else:
            print(f"❌ IVA Consulta endpoint failed: {response.status_code}")
            print(f"   - Error: {response.text}")
            
        print("\n✅ All endpoint tests completed!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Stop the server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    test_server_endpoints()
