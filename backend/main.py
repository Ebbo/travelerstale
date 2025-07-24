from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import uuid
import os
import asyncio
import time
from typing import Dict, List
from game_manager import GameManager
from models import GameAction, PlayerJoin, CharacterUpdate

app = FastAPI(title="Traveler's Tale API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create symbolic link to bgm folder if it doesn't exist
bgm_static_path = "static/bgm"
if not os.path.exists(bgm_static_path):
    os.makedirs("static", exist_ok=True)
    if os.path.exists("../bgm"):
        try:
            os.symlink("../../bgm", bgm_static_path)
        except OSError:
            # If symlink fails (Windows), copy files instead
            import shutil
            if os.path.exists("../bgm"):
                shutil.copytree("../bgm", bgm_static_path, dirs_exist_ok=True)

game_manager = GameManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.game_connections: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        disconnected_from_game = None
        
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        for game_id in self.game_connections:
            if client_id in self.game_connections[game_id]:
                self.game_connections[game_id].remove(client_id)
                disconnected_from_game = game_id
                break
        
        return disconnected_from_game

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast_to_game(self, message: str, game_id: str):
        if game_id in self.game_connections:
            for client_id in self.game_connections[game_id]:
                await self.send_personal_message(message, client_id)

manager = ConnectionManager()

async def process_actions_after_delay(game_id: str, connection_manager: ConnectionManager):
    """Process pending actions after a brief delay to show the GM working status"""
    await asyncio.sleep(2)  # Show "GM working" for 2 seconds
    result = await game_manager.process_pending_actions(game_id)
    await connection_manager.broadcast_to_game(json.dumps(result), game_id)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "join_game":
                game_id = message["game_id"]
                player_name = message["player_name"]
                
                # Check if game exists first
                game_status = await game_manager.get_game_status(game_id)
                if "error" in game_status:
                    await manager.send_personal_message(
                        json.dumps({"type": "error", "message": "Game not found"}), 
                        client_id
                    )
                    continue
                
                if game_id not in manager.game_connections:
                    manager.game_connections[game_id] = []
                
                if len(manager.game_connections[game_id]) < 6:
                    manager.game_connections[game_id].append(client_id)
                    
                    player_join = PlayerJoin(
                        player_id=client_id,
                        player_name=player_name,
                        game_id=game_id
                    )
                    
                    result = await game_manager.add_player(player_join)
                    
                    # Send personalized messages to each player
                    if game_id in manager.game_connections:
                        for connected_client_id in manager.game_connections[game_id]:
                            # Create a personalized version of the result
                            personalized_result = result.copy()
                            personalized_result["is_game_creator"] = connected_client_id == result.get("creator_id")
                            await manager.send_personal_message(json.dumps(personalized_result), connected_client_id)
                else:
                    await manager.send_personal_message(
                        json.dumps({"type": "error", "message": "Game is full"}), 
                        client_id
                    )
            
            elif message["type"] == "game_action":
                game_id = message["game_id"]
                action = GameAction(
                    player_id=client_id,
                    action_type=message["action_type"],
                    action_text=message["action_text"],
                    game_id=game_id
                )
                
                result = await game_manager.process_action(action)
                await manager.broadcast_to_game(json.dumps(result), game_id)
                
                # If all actions are received and GM is working, schedule the story processing
                if result.get("type") == "gm_working":
                    asyncio.create_task(process_actions_after_delay(game_id, manager))
            
            elif message["type"] == "start_game":
                game_id = message["game_id"]
                theme = message.get("theme", "")
                language = message.get("language", "English")
                gm_role = message.get("gm_role", "")
                chapter_length = message.get("chapter_length", "medium")
                narrator_voice = message.get("narrator_voice", "")
                
                result = await game_manager.start_game_manually(game_id, client_id, theme, language, gm_role, chapter_length, narrator_voice)
                await manager.broadcast_to_game(json.dumps(result), game_id)
            
            elif message["type"] == "chat_message":
                game_id = message["game_id"]
                chat_text = message["message"]
                player_name = message.get("player_name", "Unknown")
                
                # Broadcast chat message to all players in the game
                chat_result = {
                    "type": "chat_message",
                    "player_name": player_name,
                    "message": chat_text,
                    "timestamp": int(time.time() * 1000)  # Unix timestamp in ms
                }
                await manager.broadcast_to_game(json.dumps(chat_result), game_id)
            
            elif message["type"] == "update_character":
                game_id = message["game_id"]
                character_update = CharacterUpdate(
                    player_id=client_id,
                    game_id=game_id,
                    character_name=message.get("character_name"),
                    character_description=message.get("character_description"),
                    character_voice=message.get("character_voice")
                )
                
                result = await game_manager.update_character(character_update)
                await manager.broadcast_to_game(json.dumps(result), game_id)

    except WebSocketDisconnect:
        disconnected_game_id = manager.disconnect(client_id)
        
        if disconnected_game_id:
            # Remove player from game and notify others
            result = await game_manager.remove_player(disconnected_game_id, client_id)
            if result:
                await manager.broadcast_to_game(json.dumps(result), disconnected_game_id)

@app.post("/api/create_game")
async def create_game():
    game_id = str(uuid.uuid4())
    result = await game_manager.create_game(game_id)
    return {"game_id": game_id, "status": "created"}

@app.get("/api/game/{game_id}/status")
async def get_game_status(game_id: str):
    return await game_manager.get_game_status(game_id)

@app.get("/api/voices")
async def get_available_voices():
    return await game_manager.get_available_voices()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)