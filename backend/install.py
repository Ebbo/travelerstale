#!/usr/bin/env python3
"""
Installation script that handles dependency issues
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def install_packages():
    """Install packages one by one to avoid conflicts"""
    packages = [
        "fastapi==0.100.1",
        "uvicorn==0.23.2", 
        "websockets==11.0.3",
        "openai==1.12.0",
        "elevenlabs==0.2.26",
        "python-multipart==0.0.9",
        "python-dotenv==1.0.1",
        "aiofiles==23.2.1"
    ]
    
    # Try pydantic 2.x first, fallback to 1.x
    pydantic_packages = ["pydantic==2.6.0", "pydantic==1.10.12"]
    
    print("🔧 Installing Python packages...")
    
    # Install core packages first
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"Failed to install {package}")
            return False
    
    # Try pydantic versions
    for pydantic_pkg in pydantic_packages:
        if run_command(f"pip install {pydantic_pkg}", f"Installing {pydantic_pkg}"):
            break
    else:
        print("❌ Failed to install any compatible pydantic version")
        return False
    
    return True

def main():
    """Main installation function"""
    print("🗡️ Traveler's Tale Backend Setup")
    print("=" * 40)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment")
        print("It's recommended to create one with:")
        print("python -m venv venv")
        print("source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
        
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Install packages
    if not install_packages():
        print("\n❌ Installation failed. Try manually:")
        print("pip install fastapi uvicorn openai elevenlabs python-dotenv")
        return
    
    # Create directories
    directories = ['static/audio', 'static/bgm', 'voice_cache']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    print("\n✅ Installation completed!")
    print("\n📝 Next steps:")
    print("1. Create .env file: cp .env.example .env")
    print("2. Add your API keys to .env")
    print("3. Add background music to ../bgm folder")
    print("4. Run: python start.py")

if __name__ == "__main__":
    main()