import os
import asyncio
import aiofiles
from dotenv import load_dotenv
import random
from typing import Optional, List
import hashlib
import httpx
import time
import subprocess
import shutil

load_dotenv()

class AudioService:
    """AudioService with ElevenLabs API integration"""
    
    def __init__(self):
        self.bgm_folder = os.getenv("BGM_FOLDER_PATH", "../bgm")
        self.voice_cache_dir = "static/audio"
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.use_mock = not self.elevenlabs_api_key
        
        # Create cache directory
        os.makedirs(self.voice_cache_dir, exist_ok=True)
        
        if self.use_mock:
            print("🎭 Using Mock AudioService (no ElevenLabs API key)")
        else:
            print("🔊 Using ElevenLabs AudioService")
    
    async def generate_voice(self, text: str, language: str = "English", voice_id: Optional[str] = None, character_voices: Optional[dict] = None, narrator_voice_id: Optional[str] = None, session_language: Optional[str] = None) -> Optional[str]:
        """Generate voice using ElevenLabs with speech elements and language support"""
        if not text or len(text.strip()) == 0:
            return None
        
        # CONSISTENCY ENFORCEMENT: Use session language if provided (never change during session)
        if session_language:
            language = session_language
        
        # VOICE CONSISTENCY: Determine the narrator voice to use
        # Priority: narrator_voice_id > voice_id > default
        final_narrator_voice = None
        if narrator_voice_id and narrator_voice_id.strip():
            final_narrator_voice = narrator_voice_id.strip()
        elif voice_id and voice_id.strip():
            final_narrator_voice = voice_id.strip()
        
        print(f"🎙️ Voice Generation - Language: {language}, Narrator Voice: '{final_narrator_voice}'")
        
        # If character voices are provided and not empty, use multi-voice generation
        if character_voices and len(character_voices) > 0:
            print(f"🎭 Multi-voice generation with {len(character_voices)} character voices")
            return await self._generate_multi_voice_story(text, language, character_voices, final_narrator_voice)
        
        # Single narrator voice generation
        print(f"🔊 Single narrator voice generation")
        return await self._generate_single_narrator_voice(text, language, final_narrator_voice)
    
    async def _generate_single_narrator_voice(self, text: str, language: str, narrator_voice: Optional[str]) -> Optional[str]:
        """Generate voice for single narrator (no character dialogue)"""
        enhanced_text = self._add_speech_elements(text)
        
        # Create filename with narrator voice for proper caching
        voice_for_hash = narrator_voice or "default"
        text_hash = hashlib.md5(f"{enhanced_text}_{language}_{voice_for_hash}".encode()).hexdigest()
        filename = f"voice_{language.lower()}_{text_hash}.mp3"
        filepath = os.path.join(self.voice_cache_dir, filename)
        
        # Check cache first
        if os.path.exists(filepath):
            print(f"🔊 Using cached single voice: {filename}")
            return f"static/audio/{filename}"
        
        # Mock mode - create silent file
        if self.use_mock:
            print(f"🎭 Mock: Creating single narrator voice file")
            await self._create_test_voice_file(filepath, enhanced_text)
            return f"static/audio/{filename}"
        
        # Determine which voice to use
        if narrator_voice:
            voice_id = narrator_voice
            model_id = "eleven_multilingual_v2"
            print(f"🔒 Using session narrator voice: {voice_id}")
        else:
            voice_id, model_id = self._get_voice_for_language(language, None)
            print(f"🔒 Using language default voice: {voice_id}")
        
        try:
            print(f"🔊 Generating {language} single narrator voice...")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Adjust voice settings for better emotional expression
            data = {
                "text": enhanced_text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.4,  # Lower for more expression variety
                    "similarity_boost": 0.8,  # Higher for voice consistency
                    "style": 0.3,  # Add some style for character
                    "use_speaker_boost": True
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    # Save the audio file
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    
                    print(f"🔊 {language} voice generated successfully: {filename}")
                    return f"static/audio/{filename}"
                else:
                    print(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
                    # Fallback to test file
                    await self._create_test_voice_file(filepath, enhanced_text)
                    return f"static/audio/{filename}"
                    
        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            # Fallback to test file
            await self._create_test_voice_file(filepath, enhanced_text)
            return f"static/audio/{filename}"
    
    def _add_speech_elements(self, text: str) -> str:
        """Add ElevenLabs speech elements for emotional variety and better narration"""
        import re
        
        # Don't process if text is too short
        if len(text.strip()) < 10:
            return text
        
        enhanced_text = text
        
        # Add pauses for dramatic effect
        enhanced_text = re.sub(r'([.!?])\s+([A-Z])', r'\1 <break time="0.5s"/> \2', enhanced_text)
        enhanced_text = re.sub(r'([,;:])\s+', r'\1 <break time="0.3s"/> ', enhanced_text)
        
        # Enhance dialogue with emotional speech elements
        dialogue_patterns = [
            (r'"([^"]*?[!])"', r'"<prosody rate="fast" pitch="+2st">\1</prosody>"'),  # Excited speech
            (r'"([^"]*?[?])"', r'"<prosody pitch="+1st">\1</prosody>"'),  # Questions
            (r'"([^"]*?\.\.\.)"', r'"<prosody rate="slow">\1</prosody>"'),  # Hesitation
            (r'"([^"]*?[.])"', r'"<prosody rate="medium">\1</prosody>"'),  # Normal speech
        ]
        
        for pattern, replacement in dialogue_patterns:
            enhanced_text = re.sub(pattern, replacement, enhanced_text)
        
        # Add emphasis to important words
        emphasis_words = [
            'suddenly', 'immediately', 'warning', 'danger', 'attack', 'magic', 
            'treasure', 'ancient', 'mysterious', 'powerful', 'legendary'
        ]
        
        for word in emphasis_words:
            pattern = rf'\b({word})\b'
            replacement = rf'<emphasis level="moderate">\1</emphasis>'
            enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)
        
        # Add prosody for action descriptions
        action_patterns = [
            (r'(fights?|attacks?|strikes?|slashes?)', r'<prosody rate="fast" pitch="+1st">\1</prosody>'),
            (r'(whispers?|murmurs?)', r'<prosody volume="soft">\1</prosody>'),
            (r'(shouts?|yells?|screams?)', r'<prosody volume="loud" pitch="+2st">\1</prosody>'),
            (r'(creeps?|sneaks?|tiptoes?)', r'<prosody rate="slow" volume="soft">\1</prosody>'),
        ]
        
        for pattern, replacement in action_patterns:
            enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)
        
        # Add breathing for long narrations
        if len(enhanced_text) > 200:
            sentences = enhanced_text.split('. ')
            if len(sentences) > 3:
                # Add breath after every 2-3 sentences
                for i in range(2, len(sentences), 3):
                    if i < len(sentences):
                        sentences[i] = '<break time="0.8s"/> ' + sentences[i]
                enhanced_text = '. '.join(sentences)
        
        return enhanced_text
    
    def _get_voice_for_language(self, language: str, custom_voice_id: Optional[str] = None) -> tuple[str, str]:
        """Get appropriate voice ID and model ID for the specified language"""
        if custom_voice_id:
            # If custom voice specified, use multilingual model
            return custom_voice_id, "eleven_multilingual_v2"
        
        # Language-specific voice mappings
        language_voices = {
            "English": ("21m00Tcm4TlvDq8ikWAM", "eleven_monolingual_v1"),  # Rachel
            "Spanish": ("VR6AewLTigWG4xSOukaG", "eleven_multilingual_v2"),  # Spanish female
            "French": ("ThT5KcBeYPX3keUQqHPh", "eleven_multilingual_v2"),   # French female
            "German": ("pFZP5JQG7iQjIQuC4Bku", "eleven_multilingual_v2"),   # German female
            "Italian": ("XB0fDUnXU5q5KVOYJpqr", "eleven_multilingual_v2"),  # Italian female
            "Portuguese": ("TxGEqnHWrfWFTfGW9XjX", "eleven_multilingual_v2"), # Portuguese female
            "Polish": ("JBFqnCBsd6RMkjVDRZzb", "eleven_multilingual_v2"),   # Polish female
            "Turkish": ("PNInz6obpgDQGcFmaJgB", "eleven_multilingual_v2"),  # Turkish female
            "Russian": ("yoZ06aMxZJJ28mfd3POQ", "eleven_multilingual_v2"),  # Russian female
            "Dutch": ("flq6f7yk4E4fJM5XTYuZ", "eleven_multilingual_v2"),    # Dutch female
            "Japanese": ("pcNInz6obpgDQGcFmaJgB", "eleven_multilingual_v2"), # Japanese female
            "Chinese": ("AZnzlk1XvdvUeBnXmlld", "eleven_multilingual_v2"),  # Chinese female
            "Korean": ("yoZ06aMxZJJ28mfd3POQ", "eleven_multilingual_v2"),   # Korean female
            "Hindi": ("pFZP5JQG7iQjIQuC4Bku", "eleven_multilingual_v2"),    # Hindi female
            "Arabic": ("ThT5KcBeYPX3keUQqHPh", "eleven_multilingual_v2"),   # Arabic female
        }
        
        # Default to English if language not found
        return language_voices.get(language, language_voices["English"])
    
    async def _create_test_voice_file(self, filepath: str, text: str):
        """Create a small test MP3 file with metadata"""
        # Create a minimal silent MP3 file for testing
        # This is a valid MP3 header for a 1-second silent file
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        
        async with aiofiles.open(filepath, 'wb') as f:
            # Write a minimal MP3 structure
            await f.write(mp3_header * 100)  # Repeat to make it ~1 second
        
        print(f"🎭 Created test voice file: {os.path.basename(filepath)}")
    
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
    
    async def _generate_multi_voice_story(self, text: str, language: str, character_voices: dict, narrator_voice_id: Optional[str] = None) -> Optional[str]:
        """Generate story with multiple character voices using ElevenLabs Text to Dialogue API"""
        import re
        
        # Create unique filename including narrator voice for proper caching
        narrator_for_hash = narrator_voice_id or "default"
        text_hash = hashlib.md5(f"{text}_{language}_{str(character_voices)}_{narrator_for_hash}".encode()).hexdigest()
        filename = f"voice_multivoice_{language.lower()}_{text_hash}.mp3"
        filepath = os.path.join(self.voice_cache_dir, filename)
        
        # Check if we already have this cached
        if os.path.exists(filepath):
            print(f"🔊 Using cached multi-voice story: {filename}")
            return f"static/audio/{filename}"
        
        # Parse text into dialogue segments with appropriate voices
        dialogue_inputs = self._create_dialogue_inputs(text, character_voices, narrator_voice_id)
        
        if not dialogue_inputs or len(dialogue_inputs) <= 1:
            # Fallback to single narrator voice if no character dialogue detected
            print(f"🔊 Multi-voice fallback: No character dialogue detected, using single narrator voice")
            return await self._generate_single_narrator_voice(text, language, narrator_voice_id)
        
        if self.use_mock:
            print(f"🎭 Mock: Creating multi-voice story with dialogue API")
            await self._create_test_voice_file(filepath, text)
            return f"static/audio/{filename}"
        
        try:
            # Try Text to Dialogue API first (if available)
            print(f"🔊 Attempting multi-voice story using Text to Dialogue API...")
            
            url = "https://api.elevenlabs.io/v1/text-to-dialogue/convert"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Use the Text to Dialogue API structure
            data = {
                "inputs": dialogue_inputs,
                "model_id": "eleven_v3",  # Text to Dialogue requires v3
                "settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3
                }
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    print(f"🔊 Multi-voice dialogue generated successfully using Text to Dialogue API: {filename}")
                    return f"static/audio/{filename}"
                elif response.status_code == 404:
                    print(f"⚠️ Text to Dialogue API not available (404) - falling back to segment-based approach...")
                    return await self._generate_segment_based_multi_voice(text, language, character_voices, narrator_voice_id, filepath, filename)
                else:
                    print(f"❌ ElevenLabs Text to Dialogue API error: {response.status_code} - {response.text}")
                    print(f"🔄 Falling back to segment-based approach...")
                    return await self._generate_segment_based_multi_voice(text, language, character_voices, narrator_voice_id, filepath, filename)
                    
        except Exception as e:
            print(f"❌ Error with Text to Dialogue API: {e}")
            print(f"🔄 Falling back to segment-based approach...")
            return await self._generate_segment_based_multi_voice(text, language, character_voices, narrator_voice_id, filepath, filename)
    
    def _create_dialogue_inputs(self, text: str, character_voices: dict, narrator_voice_id: Optional[str] = None) -> List[dict]:
        """Parse text into dialogue inputs for ElevenLabs Text to Dialogue API"""
        import re
        
        if not character_voices:
            return []
        
        # Set narrator voice to Freya
        if not narrator_voice_id:
            narrator_voice_id = "pFZP5JQG7iQjIQuC4Bku"  # Freya narrator voice
            print(f"🔒 Using Freya narrator voice (default)")
        else:
            print(f"🔒 Using session narrator voice: {narrator_voice_id}")
        
        print(f"🔒 Narrator voice for dialogue generation: {narrator_voice_id}")
        
        # Create a mapping of character names to voice IDs
        char_voice_map = {}
        for player_name, voice_data in character_voices.items():
            char_name = voice_data.get('character_name', '').lower()
            voice_id = voice_data.get('voice_id')
            if char_name and voice_id:
                char_voice_map[char_name] = voice_id
        
        if not char_voice_map:
            return []
        
        dialogue_inputs = []
        
        # Split text into segments based on character speech patterns
        segments = self._parse_text_segments(text, char_voice_map)
        
        for segment in segments:
            if segment['text'].strip():
                # Add speech elements for better expression
                enhanced_text = self._add_speech_elements(segment['text'])
                
                voice_to_use = segment.get('voice_id', narrator_voice_id)
                dialogue_inputs.append({
                    "text": enhanced_text,
                    "voice_id": voice_to_use
                })
                print(f"🎭 Segment voice: {voice_to_use} ({'narrator' if voice_to_use == narrator_voice_id else 'character'})")
        
        return dialogue_inputs
    
    def _parse_text_segments(self, text: str, char_voice_map: dict) -> List[dict]:
        """Parse text into segments with voice assignments"""
        import re
        
        segments = []
        current_pos = 0
        
        # Create comprehensive patterns for all characters (including German support)
        all_patterns = []
        for char_name, voice_id in char_voice_map.items():
            escaped_name = re.escape(char_name)
            
            # Create both exact name and pronoun patterns
            name_patterns = [escaped_name]
            
            # Add common pronouns that might refer to this character
            # We'll check if the character name appears in the sentence context
            pronoun_patterns = [
                r'(?:he|she|they|er|sie)',  # English/German pronouns
                r'(?:him|her|them|ihn|ihr)',  # Object pronouns
            ]
            
            patterns = [
                # Direct speech patterns
                # "Text" says CharacterName / "Text" sagt CharacterName
                (rf'"([^"]+)"\s+(?:says?|speaks?|calls?|shouts?|whispers?|replies?|responds?|asks?|sagt|spricht|ruft|flüstert|antwortet)\s+{escaped_name}(?:\b|\.)', voice_id),
                
                # CharacterName says "Text" / CharacterName sagt "Text"
                (rf'{escaped_name}\s+(?:says?|speaks?|calls?|shouts?|whispers?|replies?|responds?|asks?|sagt|spricht|ruft|flüstert|antwortet)(?:\s*[:,])?\s*"([^"]+)"', voice_id),
                
                # CharacterName: "Text"
                (rf'{escaped_name}:\s*"([^"]+)"', voice_id),
                
                # "Text," CharacterName said / "Text," sagte CharacterName
                (rf'"([^"]+),"\s+(?:said|replied|responded|called|shouted|whispered|sagte|antwortete)\s+{escaped_name}', voice_id),
                
                # German compound verb patterns - KEY FOR YOUR EXAMPLE
                # CharacterName rief aus: "Text" / CharacterName stimmte zu: "Text"
                (rf'{escaped_name}\s+(?:rief\s+aus|stimmte\s+zu|stimmte\s+ihm\s+zu|stimmte\s+ihr\s+zu|antwortete\s+ihm|antwortete\s+ihr|rief\s+zurück|rief\s+hinüber|murmelte\s+vor\s+sich\s+hin|flüsterte\s+leise|schrie\s+laut|sagte\s+leise|sagte\s+laut):\s*"([^"]+)"', voice_id),
                
                # More German speech verbs with prepositions
                (rf'{escaped_name}\s+(?:rief|schrie|flüsterte|murmelte|seufzte|lachte|kicherte|brummte|grinste|nickte|winkte)\s+(?:aus|zu|hinüber|zurück|leise|laut|vor\s+sich\s+hin)?:?\s*"([^"]+)"', voice_id),
                
                # Narrative style patterns - key improvement for your example
                # He/She breaks... "Text" (when character name appears in context)
                (rf'(?:{escaped_name}[^.!?]*?|(?:he|she|they|er|sie)\s+[^.!?]*?)(?:breaks?|speaks?|continues?|adds?|responds?|replies?|says?|calls?|shouts?|whispers?|bricht|spricht|sagt|antwortet|ruft|flüstert)[^"]*?"([^"]+)"', voice_id),
                
                # More flexible: any sentence mentioning character name followed by quoted speech
                (rf'(?:[^.!?]*{escaped_name}[^.!?]*?"([^"]+)")', voice_id),
                
                # Character name appears before quoted text (within same sentence or nearby)
                # This catches cases where character is mentioned and then speaks without explicit speech verb
                (rf'{escaped_name}[^"]*?"([^"]+)"', voice_id),
                
                # German narrative style: Character performs action then speaks
                # E.g., "Bert sieht zur Lady Melk hinüber, seine Stimme... 'Text'"
                (rf'{escaped_name}[^"]*?(?:sieht|blickt|wendet|dreht|nickt|schaut)[^"]*?"([^"]+)"', voice_id),
                
                # Extended German patterns for complex expressions
                # CharacterName stimmte ihm zu / CharacterName agreed with him
                (rf'{escaped_name}\s+(?:stimmte\s+(?:ihm|ihr|ihnen)\s+zu|antwortete\s+(?:ihm|ihr|ihnen)|erwiderte\s+(?:ihm|ihr|ihnen)|entgegnete\s+(?:ihm|ihr|ihnen))[^"]*:\s*"([^"]+)"', voice_id),
                
                # Pronoun-based patterns when character name appears in recent context
                # This is trickier but we'll look for pronouns in sentences that follow character mentions
            ]
            
            all_patterns.extend([(p[0], voice_id, char_name) for p in patterns])
        
        # Additional context-aware pattern matching
        # Find character mentions and then look for pronouns with dialogue in nearby text
        for char_name, voice_id in char_voice_map.items():
            escaped_name = re.escape(char_name)
            
            # Find all mentions of the character name
            name_mentions = list(re.finditer(rf'\b{escaped_name}\b', text, re.IGNORECASE))
            
            for mention in name_mentions:
                # Look for quoted speech within the next 200 characters after character mention
                search_start = mention.start()
                search_end = min(mention.end() + 200, len(text))
                context_text = text[search_start:search_end]
                
                # Look for pronouns followed by actions and dialogue
                pronoun_dialogue_patterns = [
                    r'(?:he|she|they|er|sie)\s+[^"]*?"([^"]+)"',
                    r'(?:his|her|their|sein|ihr)\s+[^"]*?"([^"]+)"',
                ]
                
                for pattern in pronoun_dialogue_patterns:
                    for match in re.finditer(pattern, context_text, re.IGNORECASE):
                        full_match_start = search_start + match.start()
                        full_match_end = search_start + match.end()
                        
                        all_patterns.append((
                            text[full_match_start:full_match_end],
                            voice_id,
                            char_name,
                            full_match_start,
                            full_match_end
                        ))
        
        # Find all character speech matches
        matches = []
        print(f"🔍 Analyzing text for character voices: {list(char_voice_map.keys())}")
        print(f"🔍 Text to analyze: {text[:200]}...")
        
        for pattern_data in all_patterns:
            if len(pattern_data) == 3:  # Regular pattern
                pattern, voice_id, char_name = pattern_data
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    matched_text = match.group(0)
                    # Extract only the quoted speech from the match
                    quote_match = re.search(r'"([^"]+)"', matched_text)
                    if quote_match:
                        quoted_text = quote_match.group(1)  # Only the text inside quotes
                        print(f"✅ Found dialogue for {char_name}: \"{quoted_text[:50]}...\"")
                        matches.append({
                            'start': match.start(),
                            'end': match.end(),
                            'full_text': matched_text,  # Keep full context for positioning
                            'speech_text': quoted_text,  # Only the quoted speech
                            'voice_id': voice_id,
                            'character': char_name
                        })
                    else:
                        print(f"⚠️ No quotes found in match for {char_name}: {matched_text[:50]}...")
            else:  # Pre-computed match from context analysis
                match_text, voice_id, char_name, start, end = pattern_data
                # Extract only the quoted speech from context matches too
                quote_match = re.search(r'"([^"]+)"', match_text)
                if quote_match:
                    quoted_text = quote_match.group(1)
                    print(f"✅ Found context dialogue for {char_name}: \"{quoted_text[:50]}...\"")
                    matches.append({
                        'start': start,
                        'end': end,
                        'full_text': match_text,
                        'speech_text': quoted_text,
                        'voice_id': voice_id,
                        'character': char_name
                    })
                else:
                    print(f"⚠️ No quotes in context match for {char_name}: {match_text[:50]}...")
        
        print(f"🔍 Total matches found: {len(matches)}")
        
        # Remove overlapping matches (keep the longest/most specific one)
        matches = self._remove_overlapping_matches(matches)
        
        # Sort matches by position
        matches.sort(key=lambda x: x['start'])
        
        # Create segments with proper narrator/character separation
        for i, match in enumerate(matches):
            # Add narrator text before this character speech (including the attribution)
            if match['start'] > current_pos:
                narrator_text = text[current_pos:match['start']].strip()
                if narrator_text:
                    segments.append({
                        'text': narrator_text,
                        'voice_id': None,  # Will use narrator voice
                        'type': 'narrator'
                    })
            
            # Extract the attribution part (everything except the quoted speech)
            full_match_text = match['full_text']
            speech_text = match['speech_text']
            
            # Find the quote in the full match and separate attribution from speech
            quote_start = full_match_text.find(f'"{speech_text}"')
            if quote_start > 0:
                # Add attribution as narrator (e.g., "Melk rief aus:")
                attribution = full_match_text[:quote_start].strip()
                if attribution:
                    segments.append({
                        'text': attribution,
                        'voice_id': None,  # Narrator voice for attribution
                        'type': 'attribution'
                    })
            
            # Add only the quoted character speech
            segments.append({
                'text': speech_text,  # Only the quoted text
                'voice_id': match['voice_id'],
                'type': 'character_speech',
                'character': match['character']
            })
            
            current_pos = match['end']
        
        # Add remaining narrator text
        if current_pos < len(text):
            remaining_text = text[current_pos:].strip()
            if remaining_text:
                segments.append({
                    'text': remaining_text,
                    'voice_id': None,  # Will use narrator voice
                    'type': 'narrator'
                })
        
        # If no character speech was found, return the entire text as narrator
        if not segments:
            segments = [{
                'text': text,
                'voice_id': None,
                'type': 'narrator'
            }]
        
        return segments
    
    def _remove_overlapping_matches(self, matches: List[dict]) -> List[dict]:
        """Remove overlapping matches, keeping the most specific ones"""
        if not matches:
            return matches
        
        # Sort by start position, then by length (longer matches first)
        sorted_matches = sorted(matches, key=lambda x: (x['start'], -(x['end'] - x['start'])))
        
        filtered_matches = []
        for match in sorted_matches:
            # Check if this match overlaps with any already accepted match
            overlaps = False
            for accepted in filtered_matches:
                if (match['start'] < accepted['end'] and match['end'] > accepted['start']):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_matches.append(match)
        
        return filtered_matches
    
    async def _generate_segment_based_multi_voice(self, text: str, language: str, character_voices: dict, narrator_voice_id: Optional[str], filepath: str, filename: str) -> Optional[str]:
        """Generate multi-voice audio by creating segments and concatenating them"""
        
        print(f"🔊 Using segment-based multi-voice generation...")
        
        # Parse text into dialogue segments
        dialogue_inputs = self._create_dialogue_inputs(text, character_voices, narrator_voice_id)
        
        if not dialogue_inputs or len(dialogue_inputs) <= 1:
            # No character dialogue, use single voice
            return await self._generate_single_narrator_voice(text, language, narrator_voice_id)
        
        # Generate individual segments
        segment_files = []
        temp_dir = os.path.join(self.voice_cache_dir, "temp_segments")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            for i, segment in enumerate(dialogue_inputs):
                segment_voice_id = segment.get('voice_id', narrator_voice_id)
                segment_text = segment['text']
                
                # Generate individual segment
                segment_filename = f"segment_{i}_{hashlib.md5(segment_text.encode()).hexdigest()[:8]}.mp3"
                segment_filepath = os.path.join(temp_dir, segment_filename)
                
                # Generate audio for this segment
                success = await self._generate_individual_segment(
                    segment_text, 
                    language, 
                    segment_voice_id, 
                    segment_filepath
                )
                
                if success and os.path.exists(segment_filepath):
                    segment_files.append(segment_filepath)
                    print(f"🔊 Generated segment {i+1}/{len(dialogue_inputs)}: {segment_filename}")
                else:
                    print(f"❌ Failed to generate segment {i+1}")
            
            if not segment_files:
                print(f"❌ No segments generated successfully")
                return await self._generate_single_narrator_voice(text, language, narrator_voice_id)
            
            # Concatenate segments using ffmpeg if available, otherwise use first segment
            if len(segment_files) == 1:
                # Only one segment, just copy it
                shutil.copy2(segment_files[0], filepath)
                print(f"🔊 Single segment saved as: {filename}")
            else:
                # Try to concatenate segments
                success = await self._concatenate_audio_segments(segment_files, filepath)
                if success:
                    print(f"🔊 Multi-voice audio concatenated successfully: {filename}")
                else:
                    # Fallback: use the first segment
                    shutil.copy2(segment_files[0], filepath)
                    print(f"🔊 Concatenation failed, using first segment: {filename}")
            
            return f"static/audio/{filename}"
            
        finally:
            # Clean up temporary segment files
            for segment_file in segment_files:
                try:
                    if os.path.exists(segment_file):
                        os.remove(segment_file)
                except Exception as e:
                    print(f"⚠️ Could not clean up segment file {segment_file}: {e}")
    
    async def _generate_individual_segment(self, text: str, language: str, voice_id: str, filepath: str) -> bool:
        """Generate audio for a single text segment"""
        enhanced_text = self._add_speech_elements(text)
        
        if not voice_id:
            voice_id = "pFZP5JQG7iQjIQuC4Bku"  # Freya narrator voice
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Use multilingual model for better language support
            data = {
                "text": enhanced_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    return True
                else:
                    print(f"❌ Error generating segment: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error generating individual segment: {e}")
            return False
    
    async def _concatenate_audio_segments(self, segment_files: List[str], output_path: str) -> bool:
        """Concatenate multiple audio segments into one file"""
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            # Create ffmpeg command for concatenation
            # First, create a temporary file list
            temp_list_file = output_path + "_list.txt"
            
            with open(temp_list_file, 'w') as f:
                for segment_file in segment_files:
                    f.write(f"file '{os.path.abspath(segment_file)}'\n")
            
            # Run ffmpeg to concatenate
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output file
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_list_file,
                '-c', 'copy',  # Copy streams without re-encoding
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ ffmpeg error: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️ ffmpeg not available, cannot concatenate audio segments")
            return False
        except Exception as e:
            print(f"❌ Error concatenating segments: {e}")
            return False

    def _create_voice_tagged_text(self, text: str, character_voices: dict) -> str:
        """Create ElevenLabs voice-tagged text for character speech"""
        import re
        
        if not character_voices:
            return text
        
        # Create a mapping of character names to voice IDs
        char_voice_map = {}
        for player_name, voice_data in character_voices.items():
            char_name = voice_data.get('character_name', '').lower()
            voice_id = voice_data.get('voice_id')
            if char_name and voice_id:
                char_voice_map[char_name] = voice_id
        
        if not char_voice_map:
            return text
        
        # Process the text to add voice tags
        enhanced_text = text
        
        # Pattern 1: Direct speech with character attribution
        # "Hello there!" says John -> <voice name="john_voice_id">"Hello there!" says John</voice>
        for char_name, voice_id in char_voice_map.items():
            patterns = [
                # "Text" says CharacterName
                (rf'"([^"]+)"\s+(?:says?|speaks?|calls?|shouts?|whispers?|replies?|responds?|asks?)\s+{re.escape(char_name)}(?:\b|\.)',
                 rf'<voice name="{voice_id}">"\1" says {char_name}</voice>'),
                
                # CharacterName says "Text"
                (rf'{re.escape(char_name)}\s+(?:says?|speaks?|calls?|shouts?|whispers?|replies?|responds?|asks?)(?:\s*[:,])?\s*"([^"]+)"',
                 rf'<voice name="{voice_id}">{char_name} says "\1"</voice>'),
                
                # CharacterName: "Text" (dialogue format)
                (rf'{re.escape(char_name)}:\s*"([^"]+)"',
                 rf'<voice name="{voice_id}">{char_name}: "\1"</voice>'),
                
                # "Text," CharacterName said/replied/etc
                (rf'"([^"]+),"\s+{re.escape(char_name)}\s+(?:said|replied|responded|called|shouted|whispered)',
                 rf'<voice name="{voice_id}">"\1," {char_name} said</voice>')
            ]
            
            for pattern, replacement in patterns:
                enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text
    
    def _parse_story_segments(self, text: str, character_voices: dict) -> List[dict]:
        """Parse story text into segments with appropriate voices"""
        import re
        
        segments = []
        
        # Create a mapping of character names to voice IDs
        char_voice_map = {}
        for player_name, voice_data in character_voices.items():
            char_name = voice_data.get('character_name', '').lower()
            voice_id = voice_data.get('voice_id')
            if char_name and voice_id:
                char_voice_map[char_name] = voice_id
        
        if not char_voice_map:
            return []
        
        # Default narrator voice
        narrator_voice = "pFZP5JQG7iQjIQuC4Bku"  # Freya narrator voice
        
        # Split text into sentences for analysis
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_segment = ""
        current_voice = narrator_voice
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if this sentence contains character speech
            detected_voice = self._detect_character_voice(sentence, char_voice_map)
            
            if detected_voice != current_voice:
                # Voice change detected - save current segment
                if current_segment.strip():
                    segments.append({
                        'text': current_segment.strip(),
                        'voice_id': current_voice
                    })
                current_segment = sentence
                current_voice = detected_voice
            else:
                # Same voice - add to current segment
                current_segment += " " + sentence
        
        # Add final segment
        if current_segment.strip():
            segments.append({
                'text': current_segment.strip(),
                'voice_id': current_voice
            })
        
        return segments
    
    def _detect_character_voice(self, text: str, char_voice_map: dict) -> str:
        """Detect which character voice should be used for this text"""
        import re
        
        text_lower = text.lower()
        
        # Look for character names in the text
        for char_name, voice_id in char_voice_map.items():
            # Check for direct mentions or speech patterns
            escaped_name = re.escape(char_name)
            patterns = [
                rf'\b{escaped_name}\b.*(?:says?|speaks?|calls?|shouts?|whispers?)',
                rf'(?:says?|speaks?|calls?|shouts?|whispers?).*\b{escaped_name}\b',
                rf'"[^"]*".*\b{escaped_name}\b',
                rf'\b{escaped_name}\b.*"[^"]*"'
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return voice_id
        
        # Default to narrator voice
        return "pFZP5JQG7iQjIQuC4Bku"
    
    async def _generate_segment_audio(self, text: str, language: str, voice_id: str) -> Optional[str]:
        """Generate audio for a single segment"""
        enhanced_text = self._add_speech_elements(text)
        
        # Create filename for this segment
        text_hash = hashlib.md5(f"{enhanced_text}_{language}_{voice_id}".encode()).hexdigest()
        filename = f"voice_segment_{language.lower()}_{text_hash}.mp3"
        filepath = os.path.join(self.voice_cache_dir, filename)
        
        # Check if we already have this cached
        if os.path.exists(filepath):
            return filename
        
        if self.use_mock:
            await self._create_test_voice_file(filepath, enhanced_text)
            return filename
        
        # Generate with ElevenLabs
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": enhanced_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    return filename
                else:
                    print(f"❌ ElevenLabs API error for segment: {response.status_code}")
                    await self._create_test_voice_file(filepath, enhanced_text)
                    return filename
                    
        except Exception as e:
            print(f"❌ Error generating segment voice: {e}")
            await self._create_test_voice_file(filepath, enhanced_text)
            return filename
    
    async def _generate_single_voice(self, text: str, language: str, voice_id: Optional[str] = None) -> Optional[str]:
        """Generate single voice fallback"""
        enhanced_text = self._add_speech_elements(text)
        
        # Include voice ID in hash for proper caching
        voice_id_for_hash = voice_id or "default"
        text_hash = hashlib.md5(f"{enhanced_text}_{language}_{voice_id_for_hash}".encode()).hexdigest()
        filename = f"voice_{language.lower()}_{text_hash}.mp3"
        filepath = os.path.join(self.voice_cache_dir, filename)
        
        if os.path.exists(filepath):
            return f"static/audio/{filename}"
        
        if self.use_mock:
            await self._create_test_voice_file(filepath, enhanced_text)
            return f"static/audio/{filename}"
        
        # Preserve narrator voice consistency or use language-specific fallback
        if voice_id:
            # Use provided voice ID (narrator voice) consistently
            print(f"🔒 Using consistent narrator voice: {voice_id}")
            model_id = "eleven_multilingual_v2"  # Use multilingual for consistency
        else:
            # Only fall back to language-specific voice if no voice specified
            voice_id, model_id = self._get_voice_for_language(language, voice_id)
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": enhanced_text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    return f"static/audio/{filename}"
                else:
                    await self._create_test_voice_file(filepath, enhanced_text)
                    return f"static/audio/{filename}"
                    
        except Exception as e:
            print(f"❌ Error generating single voice: {e}")
            await self._create_test_voice_file(filepath, enhanced_text)
            return f"static/audio/{filename}"
    
    def get_available_voices(self) -> List[dict]:
        """Get available character voices optimized for German and multilingual support"""
        return [
            
            # Male Voices - German Compatible (Distinctly Different)
            {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "gender": "male", "category": "heroic", "description": "Deep, warm American voice - excellent for German"},
            {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", "gender": "male", "category": "heroic", "description": "Strong, confident voice - great for German characters"},
            {"id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam", "gender": "male", "category": "character", "description": "Young, energetic male - multilingual support"},
            {"id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", "gender": "male", "category": "character", "description": "Older, gruff character voice"},
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Ethan", "gender": "male", "category": "quirky", "description": "British accent, versatile for German"},
            {"id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie", "gender": "male", "category": "quirky", "description": "Australian accent, friendly tone"},
            
            # Female Voices - German Compatible (Distinctly Different)
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "gender": "female", "category": "heroic", "description": "Elegant British voice - excellent German pronunciation"},
            {"id": "ThT5KcBeYPX3keUQqHPh", "name": "Dorothy", "gender": "female", "category": "heroic", "description": "Warm, trustworthy - great for German"},
            {"id": "XB0fDUnXU5q5KVOYJpqr", "name": "Charlotte", "gender": "female", "category": "heroic", "description": "Sophisticated, clear pronunciation"},
            {"id": "pFZP5JQG7iQjIQuC4Bku", "name": "Freya", "gender": "female", "category": "quirky", "description": "Young, energetic - perfect for German names"},
            {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "gender": "female", "category": "quirky", "description": "Playful, expressive - multilingual"},
            {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Grace", "gender": "female", "category": "mystical", "description": "Gentle, magical tone"},
            
            # Unique Character Voices (Specialized)
            {"id": "flq6f7yk4E4fJM5XTYuZ", "name": "Fin", "gender": "neutral", "category": "mystical", "description": "Ethereal, otherworldly"},
            {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "Giovanni", "gender": "male", "category": "villain", "description": "Sophisticated antagonist voice"},
            {"id": "bVMeCyTHy58xNoL34h3p", "name": "Jeremy", "gender": "male", "category": "character", "description": "Young Irish accent - versatile"},
            {"id": "CYw3kZ02Hs0563khs1Fj", "name": "Dave", "gender": "male", "category": "character", "description": "British Essex accent - distinctive"}
        ]
    
    def cleanup_cache(self, max_files: int = 100):
        """Clean up old voice cache files"""
        print("🎭 Mock: Cache cleanup skipped")
        pass