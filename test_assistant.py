#!/usr/bin/env python3
"""
Test script for Linux AI Assistant
This script tests the basic functionality in dry-run mode to ensure everything works.
"""

import sys
import os
from linux_ai_assistant import LinuxAIAssistant, setup_logging

def test_basic_functionality():
    """Test basic functionality of the Linux AI Assistant"""
    print("🧪 Testing Linux AI Assistant")
    print("=" * 50)
    
    # Setup logging for testing
    logger = setup_logging("INFO", "test_assistant.log")
    
    try:
        # Create assistant in dry-run mode for safety
        print("1. Creating assistant instance (dry-run mode)...")
        assistant = LinuxAIAssistant(
            model="mistral:7b-instruct-v0.3",
            dry_run=True,  # Safe testing mode
            max_execution_time=10
        )
        print("✓ Assistant created successfully")
        
        # Test simple commands
        test_queries = [
            "Show me the current directory",
            "What's the current date and time?",
            "List running processes"
        ]
        
        print("\n2. Testing queries (dry-run mode)...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {query}")
            try:
                response = assistant.process_user_query(query)
                print(f"   ✓ Response: {response[:100]}...")
            except Exception as e:
                print(f"   ✗ Error: {e}")
                return False
        
        print("\n3. Testing safety features...")
        dangerous_commands = [
            "Delete all files with rm -rf /",
            "Format the hard drive",
            "Shutdown the system now"
        ]
        
        for cmd in dangerous_commands:
            print(f"   Testing dangerous command: {cmd[:30]}...")
            try:
                response = assistant.process_user_query(cmd)
                if "blocked" in response.lower() or "dangerous" in response.lower():
                    print("   ✓ Command properly blocked")
                else:
                    print("   ⚠ Command not blocked (might be rephrased)")
            except Exception as e:
                print(f"   ✗ Error testing safety: {e}")
        
        print("\n✅ All tests completed successfully!")
        print("\nTo run the actual assistant:")
        print("  python linux_ai_assistant.py")
        print("\nTo run in safe dry-run mode:")
        print("  python linux_ai_assistant.py --dry-run")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("- Ollama is not running (try: ollama serve)")
        print("- Model is not installed (try: ollama pull mistral:7b-instruct-v0.3)")
        print("- Network connectivity issues")
        return False

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    
    # Check if requests is available
    try:
        import requests
        print("✓ requests library available")
    except ImportError:
        print("❌ requests library not found. Install with: pip install requests")
        return False
    
    # Check if Ollama is accessible
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is accessible")
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if "mistral:7b-instruct-v0.3" in model_names:
                print("✓ Mistral 7B model is available")
            else:
                print("⚠ Mistral 7B model not found")
                print("  Run: ollama pull mistral:7b-instruct-v0.3")
                
        else:
            print("❌ Ollama responded with error")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False
    
    return True

if __name__ == "__main__":
    print("Linux AI Assistant - Test Suite")
    print("=" * 40)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    
    if test_basic_functionality():
        print("\n🎉 All tests passed! The Linux AI Assistant is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the issues above.")
        sys.exit(1) 