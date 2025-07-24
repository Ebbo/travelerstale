import asyncio
from typing import Dict, List, Optional
from models import GameSession, Player, GameAction, PlayerJoin, CharacterUpdate, GameState, StorySegment, ActionType
from ai_service import AIService
from audio_service import AudioService
import json

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameSession] = {}
        self.ai_service = AIService()
        self.audio_service = AudioService()

    async def create_game(self, game_id: str) -> Dict:
        game_session = GameSession(id=game_id)
        self.games[game_id] = game_session
        
        return {
            "type": "game_created",
            "game_id": game_id,
            "status": "waiting_for_players"
        }

    async def add_player(self, player_join: PlayerJoin) -> Dict:
        if player_join.game_id not in self.games:
            return {"type": "error", "message": "Game not found"}
        
        game = self.games[player_join.game_id]
        
        if len(game.players) >= 6:
            return {"type": "error", "message": "Game is full"}
        
        player = Player(
            id=player_join.player_id,
            name=player_join.player_name
        )
        
        game.players.append(player)
        
        # Set creator if this is the first player
        if len(game.players) == 1:
            game.creator_id = player.id
        
        return {
            "type": "player_joined",
            "player": player.dict(),
            "all_players": [p.dict() for p in game.players],
            "players_count": len(game.players),
            "game_state": game.state,
            "current_story": game.current_story,
            "current_player": game.players[game.current_player_turn].name if game.players and game.state != GameState.WAITING else None,
            "creator_id": game.creator_id,
            "is_game_creator": player.id == game.creator_id
        }

    async def process_action(self, action: GameAction) -> Dict:
        if action.game_id not in self.games:
            return {"type": "error", "message": "Game not found"}
        
        game = self.games[action.game_id]
        
        if game.state == GameState.WAITING:
            return {"type": "error", "message": "Game not started yet"}
        
        if game.state == GameState.STORY_TELLING:
            return {"type": "error", "message": "Please wait for the story to finish"}
        
        # Check if player has already submitted an action this round
        for pending_action in game.pending_actions:
            if pending_action.player_id == action.player_id:
                return {"type": "error", "message": "You have already submitted an action for this round"}
        
        # Check if player is valid
        player_exists = any(p.id == action.player_id for p in game.players)
        if not player_exists:
            return {"type": "error", "message": "Player not found in game"}
        
        # Add action to pending actions
        game.pending_actions.append(action)
        
        # Check if we have all actions
        if len(game.pending_actions) >= game.actions_needed:
            # Set GM working state immediately
            game.state = GameState.GM_WORKING
            
            # Return immediate status that GM is working
            return {
                "type": "gm_working",
                "message": "All actions received! The Game Master is processing what happens next...",
                "game_state": game.state,
                "actions_received": len(game.pending_actions),
                "actions_needed": game.actions_needed
            }
        else:
            # Return status update - no story yet, just background music continues
            return {
                "type": "action_received",
                "message": f"Action received from {next(p.name for p in game.players if p.id == action.player_id)}",
                "actions_received": len(game.pending_actions),
                "actions_needed": game.actions_needed,
                "waiting_for": [p.name for p in game.players if p.id not in [a.player_id for a in game.pending_actions]]
            }

    async def remove_player(self, game_id: str, player_id: str) -> Dict:
        """Remove a player who disconnected"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        # Find and remove the player
        player_to_remove = None
        for i, player in enumerate(game.players):
            if player.id == player_id:
                player_to_remove = game.players.pop(i)
                break
        
        if not player_to_remove:
            return None
        
        # If no players left, clean up the game
        if len(game.players) == 0:
            del self.games[game_id]
            return {
                "type": "game_ended",
                "message": "Game ended - all players disconnected"
            }
        
        # Adjust current player turn if needed
        if game.current_player_turn >= len(game.players):
            game.current_player_turn = 0
        
        # Remove any pending actions from the disconnected player
        game.pending_actions = [action for action in game.pending_actions if action.player_id != player_id]
        game.actions_needed = len(game.players)
        
        return {
            "type": "player_disconnected",
            "disconnected_player": player_to_remove.name,
            "remaining_players": [p.dict() for p in game.players],
            "players_count": len(game.players),
            "current_player": game.players[game.current_player_turn].name if game.players else None,
            "message": f"{player_to_remove.name} has left the adventure"
        }

    async def start_game_manually(self, game_id: str, player_id: str, theme: str = "", language: str = "English", gm_role: str = "", chapter_length: str = "medium", narrator_voice: str = "") -> Dict:
        """Start the game manually when players are ready"""
        if game_id not in self.games:
            return {"type": "error", "message": "Game not found"}
        
        game = self.games[game_id]
        
        # Only the game creator can start the game
        if game.creator_id != player_id:
            return {"type": "error", "message": "Only the game creator can start the adventure"}
        
        if len(game.players) < 1:
            return {"type": "error", "message": "Need at least 1 player to start"}
        
        if game.state != GameState.WAITING:
            return {"type": "error", "message": "Game already started"}
        
        # Store game settings (lock them for the session)
        game.language = language
        game.theme = theme
        game.gm_role = gm_role
        game.chapter_length = chapter_length
        
        # Always use Freya as narrator voice
        game.narrator_voice = "pFZP5JQG7iQjIQuC4Bku"  # Freya
        print(f"🔒 Using Freya as narrator voice")
        
        print(f"🔒 Game settings locked for session - Language: {language}, Narrator: {game.narrator_voice}")
        
        voice_file, bgm_file = await self._start_game(game, theme, language, gm_role, chapter_length)
        
        return {
            "type": "game_started",
            "message": "Adventure begins!",
            "current_story": game.current_story,
            "current_player": "All players" if len(game.players) > 1 else game.players[0].name,
            "game_state": game.state,
            "voice_file": voice_file,
            "background_music": bgm_file,
            "actions_needed": len(game.players),
            "actions_received": 0
        }

    async def _start_game(self, game: GameSession, theme: str = "", language: str = "English", gm_role: str = "", chapter_length: str = "medium"):
        game.state = GameState.STORY_TELLING
        
        theme_instruction = f"Theme: {theme}. " if theme else ""
        language_instruction = f"Write the story in {language}. " if language != "English" else ""
        
        # Chapter length instructions
        length_instructions = {
            "short": "Keep chapters brief and focused (1-2 paragraphs). Move quickly between action points.",
            "medium": "Use moderate pacing with 2-3 paragraphs per chapter. Balance description and action.",
            "long": "Create detailed, immersive chapters (3-4 paragraphs). Include rich descriptions and character development."
        }
        length_instruction = length_instructions.get(chapter_length, length_instructions["medium"])
        
        # Build character context for story generation
        character_context = self._build_character_context(game)
        
        initial_prompt = f"""
        You are the Game Master for an interactive adventure with {len(game.players)} players: {', '.join([p.name for p in game.players])}.
        
        {language_instruction}{theme_instruction}Start an engaging adventure story. Set the scene, introduce the world, and create an interesting situation where the players need to make decisions or take actions.
        
        CHAPTER LENGTH: {length_instruction}
        
        {character_context}
        
        The story should be immersive and leave room for player agency. End with a situation where the players need to decide what to do.
        
        Keep the story appropriate for all audiences and focus on adventure, exploration, and problem-solving.
        """
        
        story_response = await self.ai_service.generate_story(initial_prompt, game.scene_context, gm_role)
        game.current_story = story_response["story"]
        game.scene_context = story_response["context"]
        
        # Prepare character voices for multi-voice generation
        character_voices = self._get_character_voices(game)
        
        # Generate voice for the story using consistent session settings
        voice_file = await self.audio_service.generate_voice(
            story_response["story"], 
            language,
            character_voices=character_voices,
            narrator_voice_id=game.narrator_voice,
            session_language=game.language
        )
        
        # Select background music
        bgm_file = await self.audio_service.select_background_music("adventure")
        
        story_segment = StorySegment(
            text=story_response["story"],
            voice_file=voice_file,
            background_music=bgm_file
        )
        game.story_history.append(story_segment)
        
        # Set up round-based gameplay
        game.state = GameState.PLAYER_TURN
        game.current_player_turn = 0
        game.actions_needed = len(game.players)
        game.pending_actions = []
        
        return voice_file, bgm_file

    async def process_pending_actions(self, game_id: str) -> Dict:
        """Process all pending actions for a game that's in GM_WORKING state"""
        if game_id not in self.games:
            return {"type": "error", "message": "Game not found"}
        
        game = self.games[game_id]
        
        if game.state != GameState.GM_WORKING:
            return {"type": "error", "message": "Game is not in GM working state"}
        
        return await self._process_all_actions(game)

    async def update_character(self, character_update: CharacterUpdate) -> Dict:
        """Update a player's character information (with voice consistency enforcement)"""
        if character_update.game_id not in self.games:
            return {"type": "error", "message": "Game not found"}
        
        game = self.games[character_update.game_id]
        
        # Find the player and update their character info
        for player in game.players:
            if player.id == character_update.player_id:
                # Allow updates to name, description, and gender
                if character_update.character_name is not None:
                    player.character_name = character_update.character_name
                if character_update.character_description is not None:
                    player.character_description = character_update.character_description
                if character_update.character_gender is not None:
                    player.character_gender = character_update.character_gender
                
                # VOICE CONSISTENCY: Only allow voice change if not set yet or game hasn't started
                if character_update.character_voice is not None:
                    if player.character_voice is None or game.state == GameState.WAITING:
                        # Allow voice setting/changing only before game starts or if not set
                        if character_update.character_voice.strip():
                            player.character_voice = character_update.character_voice.strip()
                            print(f"🔒 Character voice set for {player.name}: {player.character_voice}")
                        else:
                            player.character_voice = None
                            print(f"🔒 Character voice cleared for {player.name}")
                    else:
                        print(f"⚠️ Voice locked for {player.name} - game in progress")
                
                return {
                    "type": "character_updated",
                    "player_id": character_update.player_id,
                    "character_name": player.character_name,
                    "character_description": player.character_description,
                    "character_voice": player.character_voice,
                    "character_gender": player.character_gender,
                    "all_players": [p.dict() for p in game.players],
                    "voice_locked": game.state != GameState.WAITING
                }
        
        return {"type": "error", "message": "Player not found"}

    async def get_available_voices(self) -> Dict:
        """Get list of available character voices"""
        voices = self.audio_service.get_available_voices()
        return {
            "type": "voices_list",
            "voices": voices
        }
    
    def _get_character_voices(self, game: GameSession) -> dict:
        """Get character voices mapping for multi-voice generation"""
        character_voices = {}
        
        for player in game.players:
            if player.character_name and player.character_voice:
                character_voices[player.name] = {
                    'character_name': player.character_name,
                    'voice_id': player.character_voice
                }
        
        print(f"🎭 Active character voices: {len(character_voices)} players with voice settings")
        return character_voices
    
    def _build_character_context(self, game: GameSession) -> str:
        """Build character context for story generation"""
        if not game.players:
            return ""
        
        character_descriptions = []
        for player in game.players:
            if player.character_name:
                char_info = f"- {player.character_name}"
                
                # Add gender information
                if player.character_gender:
                    char_info += f" ({player.character_gender})"
                
                # Add character description
                if player.character_description:
                    char_info += f": {player.character_description}"
                else:
                    char_info += f": A {player.character_gender or 'character'} adventurer"
                
                character_descriptions.append(char_info)
        
        if character_descriptions:
            return f"""

CHARACTER ROSTER:
{chr(10).join(character_descriptions)}

IMPORTANT: Use these character descriptions to inform your storytelling. Reference their abilities, personalities, and backgrounds when they act or when situations would be relevant to their skills."""
        
        return ""

    async def _process_all_actions(self, game: GameSession) -> Dict:
        """Process all collected player actions and generate the next story"""
        game.state = GameState.STORY_TELLING
        
        # Create combined context for all actions with character information
        actions_summary = []
        for action in game.pending_actions:
            player = next(p for p in game.players if p.id == action.player_id)
            char_name = player.character_name or player.name
            action_desc = f"{char_name} wants to {action.action_text} (Type: {action.action_type})"
            actions_summary.append(action_desc)
        
        character_context = self._build_character_context(game)
        
        # Include language instruction to maintain consistency
        language_instruction = f"Write the story in {game.language}. " if game.language != "English" else ""
        
        # Include theme instruction for consistency
        theme_instruction = f"Theme: {game.theme}. " if game.theme else ""
        
        # Include chapter length instruction for consistency
        length_instructions = {
            "short": "Keep chapters brief and focused (1-2 paragraphs). Move quickly between action points.",
            "medium": "Use moderate pacing with 2-3 paragraphs per chapter. Balance description and action.",
            "long": "Create detailed, immersive chapters (3-4 paragraphs). Include rich descriptions and character development."
        }
        length_instruction = length_instructions.get(game.chapter_length, length_instructions["medium"])
        
        context = f"""
        {language_instruction}{theme_instruction}Continue the adventure story for {len(game.players)} players.
        
        CHAPTER LENGTH: {length_instruction}
        
        Current scene: {game.scene_context}
        Previous story: {game.current_story}
        
        {character_context}
        
        All players have submitted their actions:
        {chr(10).join(actions_summary)}
        
        Continue the story based on ALL these actions happening simultaneously or in sequence. 
        Describe what happens as a result of the players' combined actions.
        Include consequences, new developments, or challenges.
        
        Consider each character's abilities, personality, and background when describing their actions and their results.
        
        If any actions lead to combat, indicate that combat has begun.
        If the actions resolve the current situation, set up the next scenario.
        
        End with a new situation that requires all players to decide their next actions.
        """
        
        print(f"🔒 Processing actions - Narrator Voice: '{game.narrator_voice}', Language: {game.language}")
        story_response = await self.ai_service.generate_story(context, game.scene_context, game.gm_role)
        
        # Determine if we're entering combat
        if "combat" in story_response.get("scene_type", "").lower():
            game.state = GameState.COMBAT
            bgm_type = "combat"
        else:
            game.state = GameState.PLAYER_TURN
            bgm_type = "adventure"
        
        # Prepare character voices for multi-voice generation
        character_voices = self._get_character_voices(game)
        
        # Generate voice using consistent session settings
        voice_file = await self.audio_service.generate_voice(
            story_response["story"], 
            game.language,
            character_voices=character_voices,
            narrator_voice_id=game.narrator_voice,
            session_language=game.language
        )
        bgm_file = await self.audio_service.select_background_music(bgm_type)
        
        # Update game state
        game.current_story = story_response["story"]
        game.scene_context = story_response["context"]
        
        story_segment = StorySegment(
            text=story_response["story"],
            voice_file=voice_file,
            background_music=bgm_file
        )
        game.story_history.append(story_segment)
        
        # Reset for next round
        game.pending_actions = []
        game.actions_needed = len(game.players)
        
        return {
            "type": "story_update",
            "story": story_response["story"],
            "voice_file": voice_file,
            "background_music": bgm_file,
            "current_player": "All players",
            "game_state": game.state,
            "actions_processed": [
                {
                    "player": next(p.name for p in game.players if p.id == action.player_id),
                    "action": action.action_text,
                    "type": action.action_type
                } for action in game.pending_actions
            ],
            "actions_needed": game.actions_needed,
            "actions_received": 0
        }


    async def get_game_status(self, game_id: str) -> Dict:
        if game_id not in self.games:
            return {"error": "Game not found"}
        
        game = self.games[game_id]
        return {
            "game_id": game_id,
            "state": game.state,
            "players": [p.dict() for p in game.players],
            "current_player": game.players[game.current_player_turn].name if game.players else None,
            "current_story": game.current_story
        }