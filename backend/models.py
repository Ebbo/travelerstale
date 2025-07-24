from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum

class ActionType(str, Enum):
    SPEAK = "speak"
    ACTION = "action"
    ATTACK = "attack"
    DEFEND = "defend"
    CAST_SPELL = "cast_spell"
    USE_ITEM = "use_item"

class GameState(str, Enum):
    WAITING = "waiting"
    STORY_TELLING = "story_telling"
    GM_WORKING = "gm_working"
    PLAYER_TURN = "player_turn"
    COMBAT = "combat"
    PAUSED = "paused"

class Player(BaseModel):
    id: str
    name: str
    character_name: Optional[str] = None
    character_description: Optional[str] = None
    character_voice: Optional[str] = None
    character_gender: Optional[str] = None  # "male" or "female"
    is_active: bool = True

class GameAction(BaseModel):
    player_id: str
    action_type: ActionType
    action_text: str
    game_id: str

class PlayerJoin(BaseModel):
    player_id: str
    player_name: str
    game_id: str

class CharacterUpdate(BaseModel):
    player_id: str
    game_id: str
    character_name: Optional[str] = None
    character_description: Optional[str] = None
    character_voice: Optional[str] = None
    character_gender: Optional[str] = None  # "male" or "female"

class StorySegment(BaseModel):
    text: str
    voice_file: Optional[str] = None
    background_music: Optional[str] = None

class GameSession(BaseModel):
    id: str
    players: List[Player] = []
    creator_id: Optional[str] = None
    current_story: str = ""
    story_history: List[StorySegment] = []
    current_player_turn: int = 0
    state: GameState = GameState.WAITING
    background_music: Optional[str] = None
    scene_context: str = ""
    language: str = "English"
    theme: str = ""
    gm_role: str = ""
    chapter_length: str = "medium"  # short, medium, long
    narrator_voice: str = "pFZP5JQG7iQjIQuC4Bku"  # Freya narrator voice
    pending_actions: List[GameAction] = []
    actions_needed: int = 0