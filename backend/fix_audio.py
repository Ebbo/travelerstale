#!/usr/bin/env python3
"""
Script to fix audio service based on ElevenLabs version
"""

import os
import shutil

def backup_current():
    """Backup current audio service"""
    if os.path.exists("audio_service.py"):
        shutil.copy("audio_service.py", "audio_service_backup.py")
        print("✅ Backed up current audio_service.py")

def use_simple_version():
    """Use the simplified ElevenLabs version"""
    if os.path.exists("audio_service_simple.py"):
        shutil.copy("audio_service_simple.py", "audio_service.py")
        print("✅ Using simplified ElevenLabs version")
        return True
    return False

def use_mock_version():
    """Use the mock version (no ElevenLabs)"""
    if os.path.exists("audio_service_mock.py"):
        shutil.copy("audio_service_mock.py", "audio_service.py")
        print("✅ Using mock version (no voice generation)")
        return True
    return False

def main():
    print("🔧 Audio Service Fix Tool")
    print("=" * 30)
    
    backup_current()
    
    print("\nChoose an option:")
    print("1. Test ElevenLabs compatibility")
    print("2. Use simplified ElevenLabs version")  
    print("3. Use mock version (no voice generation)")
    print("4. Restore backup")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\nRunning ElevenLabs test...")
        os.system("python test_elevenlabs.py")
        
    elif choice == "2":
        if use_simple_version():
            print("✅ Now using simplified ElevenLabs version")
            print("Try running the server again!")
        else:
            print("❌ Simple version file not found")
            
    elif choice == "3":
        if use_mock_version():
            print("✅ Now using mock version (no voice generation)")
            print("The game will work without voice synthesis")
            print("Try running the server again!")
        else:
            print("❌ Mock version file not found")
            
    elif choice == "4":
        if os.path.exists("audio_service_backup.py"):
            shutil.copy("audio_service_backup.py", "audio_service.py")
            print("✅ Restored backup")
        else:
            print("❌ No backup found")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()