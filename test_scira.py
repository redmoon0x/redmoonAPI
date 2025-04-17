#!/usr/bin/env python3
"""
Test script for Scira.ai Chat Client

This script tests the Scira.ai chat client to ensure it's working properly.
"""

import sys
import json
from simple_scira_chat import SciraChat

def test_model(model_name):
    """Test a specific Scira model."""
    print(f"\n=== Testing {model_name} model ===")
    
    # Create a new instance
    client = SciraChat(model=model_name)
    
    # Test cookie refresh
    print("Refreshing cookies...")
    cookies_result = client._refresh_cookies()
    print(f"Cookies refreshed: {cookies_result}")
    
    # Test chat
    test_message = "Hello, can you give me a very short response?"
    print(f"Sending test message: '{test_message}'")
    
    response = client.chat(test_message)
    
    if response:
        print(f"Response received ({len(response)} characters):")
        print("-" * 40)
        print(response)
        print("-" * 40)
        return True
    else:
        print("No response received!")
        return False

def main():
    """Main test function."""
    print("=== Scira.ai Chat Client Test ===")
    
    # Test all models
    models = ["default", "grok", "claude", "vision"]
    results = {}
    
    for model in models:
        print(f"\nTesting {model} model...")
        success = test_model(model)
        results[model] = "SUCCESS" if success else "FAILED"
    
    # Print summary
    print("\n=== Test Results ===")
    for model, result in results.items():
        print(f"{model}: {result}")
    
    # Return non-zero exit code if any test failed
    if "FAILED" in results.values():
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
