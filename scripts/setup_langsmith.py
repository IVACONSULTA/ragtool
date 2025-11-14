#!/usr/bin/env python3
"""
LangSmith Setup Script

This script helps you set up LangSmith integration for the SapRagTool.
It checks your configuration and provides guidance on getting started.

Usage:
    python scripts/setup_langsmith.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.utils.config import get_langsmith_config, print_config_info
from agents.langsmith_integration import get_langsmith_manager


def check_environment():
    """Check if LangSmith environment variables are set."""
    print("🔍 Checking LangSmith environment configuration...")
    
    required_vars = {
        "LANGSMITH_API_KEY": "LangSmith API key",
        "LANGSMITH_PROJECT": "LangSmith project name (optional, defaults to 'sap-rag-tool-dev')",
        "LANGCHAIN_TRACING_V2": "Enable tracing (optional, defaults to 'true')"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if var == "LANGSMITH_API_KEY" and not value:
            missing_vars.append(f"❌ {var}: {description}")
        elif value:
            print(f"✅ {var}: {description} = {value}")
        else:
            print(f"⚠️  {var}: {description} (not set, using default)")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    print("✅ All environment variables are properly configured")
    return True


def test_langsmith_connection():
    """Test LangSmith connection and configuration."""
    print("\n🔍 Testing LangSmith connection...")
    
    try:
        manager = get_langsmith_manager()
        
        if not manager.is_enabled():
            print("❌ LangSmith is not enabled")
            print("   Make sure LANGSMITH_API_KEY is set correctly")
            return False
        
        client = manager.get_client()
        if not client:
            print("❌ LangSmith client is not available")
            return False
        
        config = manager.config
        print(f"✅ LangSmith connection successful")
        print(f"   Project: {config.get('project', 'N/A')}")
        print(f"   API Key: {'Set' if config.get('api_key') else 'Not set'}")
        print(f"   Endpoint: {config.get('endpoint', 'Default')}")
        
        return True
        
    except Exception as e:
        print(f"❌ LangSmith connection failed: {e}")
        return False


def show_setup_instructions():
    """Show setup instructions for LangSmith."""
    print("\n📋 LangSmith Setup Instructions:")
    print("=" * 50)
    
    print("\n1. Get LangSmith API Key:")
    print("   • Go to https://smith.langchain.com/")
    print("   • Sign up or log in")
    print("   • Go to Settings → API Keys")
    print("   • Create a new API key")
    print("   • Copy the API key")
    
    print("\n2. Set Environment Variables:")
    print("   For local development (.env file):")
    print("   LANGSMITH_API_KEY=your_api_key_here")
    print("   LANGSMITH_PROJECT=sap-rag-tool")
    print("   LANGCHAIN_TRACING_V2=true")
    
    print("\n   For Railway deployment:")
    print("   • Go to your Railway project dashboard")
    print("   • Go to Variables tab")
    print("   • Add the environment variables above")
    
    print("\n3. Deploy and Test:")
    print("   • Deploy your application")
    print("   • Check health endpoint: GET /health")
    print("   • Look for 'langsmith' status in response")
    
    print("\n4. View Traces:")
    print("   • Go to https://smith.langchain.com/")
    print("   • Select your project")
    print("   • View traces in real-time")


def show_current_config():
    """Show current configuration."""
    print("\n🔧 Current Configuration:")
    print("=" * 30)
    
    try:
        print_config_info()
    except Exception as e:
        print(f"❌ Error getting configuration: {e}")


def main():
    """Main setup function."""
    print("🚀 LangSmith Setup for SapRagTool")
    print("=" * 40)
    
    # Check environment
    env_ok = check_environment()
    
    # Test connection if environment is OK
    if env_ok:
        connection_ok = test_langsmith_connection()
        
        if connection_ok:
            print("\n🎉 LangSmith is properly configured and working!")
            print("   You can now monitor your agent in the LangSmith dashboard")
        else:
            print("\n⚠️  Environment variables are set but connection failed")
            print("   Check your API key and network connectivity")
    else:
        print("\n📋 Follow the setup instructions below to configure LangSmith")
        show_setup_instructions()
    
    # Always show current config
    show_current_config()
    
    print("\n" + "=" * 40)
    print("Setup check complete!")


if __name__ == "__main__":
    main()
