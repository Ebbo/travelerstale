#!/usr/bin/env python3
"""
Test script to check ElevenLabs API compatibility
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs():
    """Test different ElevenLabs import methods"""
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in .env")
        return False
    
    print("🧪 Testing ElevenLabs API...")
    
    # Test method 1: New client-based API
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        print("✅ Method 1: Client-based import works")
        
        # Test voice generation
        try:
            audio = client.generate(
                text="Hello, this is a test.",
                voice="21m00Tcm4TlvDq8ikWAM",  # Rachel
                model="eleven_monolingual_v1"
            )
            print("✅ Method 1: Voice generation works")
            return True
        except Exception as e:
            print(f"❌ Method 1: Voice generation failed: {e}")
    except Exception as e:
        print(f"❌ Method 1: Client import failed: {e}")
    
    # Test method 2: Legacy function-based API
    try:
        from elevenlabs import generate, save
        print("✅ Method 2: Legacy imports work")
        
        # Test voice generation
        try:
            audio = generate(
                text="Hello, this is a test.",
                voice="21m00Tcm4TlvDq8ikWAM",
                api_key=api_key
            )
            print("✅ Method 2: Legacy voice generation works")
            return True
        except Exception as e:
            print(f"❌ Method 2: Legacy voice generation failed: {e}")
    except Exception as e:
        print(f"❌ Method 2: Legacy imports failed: {e}")
    
    # Test method 3: Simple client
    try:
        import elevenlabs
        elevenlabs.set_api_key(api_key)
        print("✅ Method 3: Simple API key setting works")
        
        # Test voice generation
        try:
            audio = elevenlabs.generate(
                text="Hello, this is a test.",
                voice="21m00Tcm4TlvDq8ikWAM"
            )
            print("✅ Method 3: Simple voice generation works")
            return True
        except Exception as e:
            print(f"❌ Method 3: Simple voice generation failed: {e}")
    except Exception as e:
        print(f"❌ Method 3: Simple API failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🗡️ ElevenLabs API Test")
    print("=" * 30)
    
    if test_elevenlabs():
        print("\n✅ ElevenLabs API is working!")
    else:
        print("\n❌ All ElevenLabs methods failed.")
        print("\nTroubleshooting:")
        print("1. Check your API key in .env")
        print("2. Try: pip install --upgrade elevenlabs")
        print("3. Check ElevenLabs API documentation for changes")