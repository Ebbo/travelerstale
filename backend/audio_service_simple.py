import os
import asyncio
import aiofiles
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import random
from typing import Optional, List
import hashlib

load_dotenv()

class AudioService:
    def __init__(self):
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.bgm_folder = os.getenv("BGM_FOLDER_PATH", "../bgm")
        self.voice_cache_dir = "static/audio"
        
        # Create cache directory
        os.makedirs(self.voice_cache_dir, exist_ok=True)
        
        # Default voice ID (Rachel)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"
    
    async def generate_voice(self, text: str, voice_id: Optional[str] = None) -> str:
        """Generate voice audio from text using ElevenLabs"""
        if not text.strip():
            return None
            
        # Create a hash of the text for caching
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_filename = f"{self.voice_cache_dir}/voice_{text_hash}.mp3"
        # Return the relative path for the frontend to access
        relative_path = f"static/audio/voice_{text_hash}.mp3"
        
        # Check if we already have this audio cached
        if os.path.exists(cache_filename):
            return relative_path
        
        try:
            # Use default voice if none specified
            voice_to_use = voice_id or self.default_voice_id
            
            # Generate audio using the simplified API
            audio = self.elevenlabs_client.generate(
                text=text,
                voice=voice_to_use,
                model="eleven_monolingual_v1"
            )
            
            # Save to cache
            with open(cache_filename, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            return relative_path
            
        except Exception as e:
            print(f"Error generating voice: {e}")
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
        """Get list of available ElevenLabs voices"""
        try:
            # Try the new API first
            try:
                voice_list = self.elevenlabs_client.voices.get_all()
                return [{"id": voice.voice_id, "name": voice.name} for voice in voice_list.voices]
            except:
                # Fallback for older API
                voice_list = self.elevenlabs_client.voices.get()
                return [{"id": voice.voice_id, "name": voice.name} for voice in voice_list]
        except Exception as e:
            print(f"Error getting voices: {e}")
            return [{"id": self.default_voice_id, "name": "Rachel (Default)"}]
    
    def cleanup_cache(self, max_files: int = 100):
        """Clean up old voice cache files"""
        try:
            if not os.path.exists(self.voice_cache_dir):
                return
            
            cache_files = [
                os.path.join(self.voice_cache_dir, f) 
                for f in os.listdir(self.voice_cache_dir)
                if f.endswith('.mp3')
            ]
            
            if len(cache_files) > max_files:
                # Sort by modification time and remove oldest files
                cache_files.sort(key=os.path.getmtime)
                files_to_remove = cache_files[:-max_files]
                
                for file_path in files_to_remove:
                    os.remove(file_path)
                    
                print(f"Cleaned up {len(files_to_remove)} old voice cache files")
                
        except Exception as e:
            print(f"Error cleaning cache: {e}")