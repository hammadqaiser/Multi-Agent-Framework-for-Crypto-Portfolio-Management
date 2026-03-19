"""Test script to verify setup."""
import sys
import os

def test_imports():
    """Test if all major imports work."""
    try:
        import openai
        print(" OpenAI imported")
        
        import pandas as pd
        print("Pandas imported")
        
        import numpy as np
        print("NumPy imported")
        
        # Test crypto libraries
        import ccxt
        print("CCXT imported")
        
        from pycoingecko import CoinGeckoAPI
        print("CoinGecko imported")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"\nImport failed: {e}")
        return False

def test_environment():
    """Test environment setup."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"Missing environment variables: {missing}")
        print("   Add them to .env file")
    else:
        print("Environment variables configured")

if __name__ == "__main__":
    print("Testing setup...\n")
    test_imports()
    test_environment()
    print("\nSetup verification complete!")