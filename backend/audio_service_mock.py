import os
import asyncio
import aiofiles
from dotenv import load_dotenv
import random
from typing import Optional, List
import hashlib

load_dotenv()

class AudioService:
    """Mock AudioService for testing without ElevenLabs"""
    
    def __init__(self):
        self.bgm_folder = os.getenv("BGM_FOLDER_PATH", "../bgm")
        self.voice_cache_dir = "static/audio"
        
        # Create cache directory
        os.makedirs(self.voice_cache_dir, exist_ok=True)
        
        print("🎭 Using Mock AudioService (no voice generation)")
    
    async def generate_voice(self, text: str, voice_id: Optional[str] = None) -> str:
        """Mock voice generation - returns None to skip voice"""
        print(f"🎭 Mock: Would generate voice for: {text[:50]}...")
        return None
    
    async def select_background_music(self, scene_type: str) -> Optional[str]:
        """Select appropriate background music based on scene type"""
        if not os.path.exists(self.bgm_folder):
            print(f"BGM folder not found: {self.bgm_folder}")
            return None
        
        # Get all audio files from BGM folder
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
        bgm_files = []
        
        try:
            for file in os.listdir(self.bgm_folder):
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    bgm_files.append(os.path.join(self.bgm_folder, file))
        except Exception as e:
            print(f"Error reading BGM folder: {e}")
            return None
        
        if not bgm_files:
            print("No background music files found")
            return None
        
        # Select music based on scene type
        selected_file = self._select_music_by_scene(bgm_files, scene_type)
        
        # Return relative path for frontend access
        if selected_file:
            filename = os.path.basename(selected_file)
            return f"static/bgm/{filename}"
        
        return None
    
    def _select_music_by_scene(self, bgm_files: List[str], scene_type: str) -> str:
        """Select appropriate music file based on scene type"""
        # Keywords to match in filenames
        scene_keywords = {
            "combat": ["combat", "battle", "fight", "war", "boss", "action", "intense"],
            "dialog": ["calm", "peaceful", "quiet", "ambient", "soft", "gentle"],
            "exploration": ["mystery", "adventure", "explore", "dungeon", "forest", "ambient"],
            "adventure": ["adventure", "journey", "travel", "theme", "main"]
        }
        
        keywords = scene_keywords.get(scene_type, scene_keywords["adventure"])
        
        # First try to find files matching scene keywords
        matching_files = []
        for file in bgm_files:
            filename_lower = os.path.basename(file).lower()
            if any(keyword in filename_lower for keyword in keywords):
                matching_files.append(file)
        
        # If no matching files found, use any available file
        if not matching_files:
            matching_files = bgm_files
        
        return random.choice(matching_files)
    
    def get_available_voices(self) -> List[dict]:
        """Mock voice list"""
        return [
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (Mock)"},
            {"id": "mock_voice_1", "name": "Mock Voice 1"},
            {"id": "mock_voice_2", "name": "Mock Voice 2"}
        ]
    
    def cleanup_cache(self, max_files: int = 100):
        """Clean up old voice cache files"""
        print("🎭 Mock: Cache cleanup skipped")
        pass