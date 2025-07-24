#!/usr/bin/env python3
"""
Startup script for Traveler's Tale backend server
"""

import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with your API keys:")
        print("   cp .env.example .env")
        print("   # Then edit .env with your actual API keys")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/audio',
        'static/bgm', 
        'voice_cache',
        '../bgm'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_bgm_folder():
    """Check if background music folder exists and has files"""
    bgm_folder = Path('../bgm')
    
    if not bgm_folder.exists():
        print("⚠️  Background music folder not found at ../bgm")
        print("   Creating folder... Please add your music files there.")
        bgm_folder.mkdir(exist_ok=True)
        return
    
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(list(bgm_folder.glob(f'*{ext}')))
        audio_files.extend(list(bgm_folder.glob(f'*{ext.upper()}')))
    
    if audio_files:
        print(f"🎵 Found {len(audio_files)} background music files:")
        for file in audio_files[:5]:  # Show first 5 files
            print(f"   - {file.name}")
        if len(audio_files) > 5:
            print(f"   ... and {len(audio_files) - 5} more")
    else:
        print("⚠️  No background music files found in ../bgm")
        print("   Supported formats: MP3, WAV, OGG, M4A")
        print("   The game will work without music, but it's more fun with it!")

def main():
    """Main startup function"""
    print("🗡️  Starting Traveler's Tale Backend Server")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    print("✓ Environment variables configured")
    
    # Create necessary directories
    create_directories()
    
    # Check background music
    check_bgm_folder()
    
    print("=" * 50)
    print("🚀 Starting server...")
    print("📍 Backend: http://localhost:8000")
    print("🎮 Start the frontend with: cd ../frontend && npm run dev")
    print("⏹️  Stop server with: Ctrl+C")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()