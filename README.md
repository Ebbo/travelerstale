# 🗡️ Traveler's Tale

An AI-powered collaborative storytelling service where up to 6 players can come together with an AI Game Master to create epic adventures. Features real-time voice narration, background music, and turn-based gameplay.

## Features

- **AI-Powered Storytelling**: Uses OpenAI GPT-4 to generate dynamic, engaging stories
- **Voice Narration**: ElevenLabs AI voice synthesis for immersive storytelling
- **Background Music**: Dynamic music selection based on story context (adventure, combat, dialog)
- **Real-time Multiplayer**: Up to 6 players can participate simultaneously
- **Turn-based Actions**: Players take turns performing actions that influence the story
- **Rich Web Interface**: Beautiful Svelte frontend with real-time updates

## Tech Stack

### Backend (Python)
- **FastAPI**: Web framework with WebSocket support
- **OpenAI API**: GPT-4 for story generation
- **ElevenLabs API**: AI voice synthesis
- **Pygame**: Audio playback system
- **WebSockets**: Real-time communication

### Frontend (Svelte)
- **SvelteKit**: Modern web framework
- **TypeScript**: Type-safe development
- **WebSocket**: Real-time game updates
- **Responsive Design**: Works on desktop and mobile

## Setup Instructions

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- OpenAI API key
- ElevenLabs API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**If you encounter pydantic-core build errors**, try the alternative installation:
```bash
python install.py
```

Or install packages individually:
```bash
pip install fastapi uvicorn openai elevenlabs python-dotenv aiofiles
```

4. Create a `.env` file with your API keys:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
BGM_FOLDER_PATH=../bgm
```

5. Create directories for audio files:
```bash
mkdir -p static/audio static/bgm voice_cache
```

6. Add background music files to the `bgm` folder (MP3, WAV, OGG, M4A formats supported)

7. Start the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## How to Play

1. **Create a Game**: Click "Create Game" on the homepage to start a new adventure
2. **Share Game ID**: Share the generated Game ID with up to 5 friends
3. **Join Game**: Players enter the Game ID and their name to join
4. **Adventure Begins**: The AI Game Master starts the story once players join
5. **Take Turns**: Players take turns describing their actions
6. **Enjoy**: Listen to AI narration and enjoy dynamic background music

## Game Actions

Players can perform different types of actions:

- **💬 Speak**: Dialog with NPCs or other players
- **⚡ Action**: General actions like exploring, investigating
- **⚔️ Attack**: Combat actions against enemies
- **🛡️ Defend**: Defensive actions and blocking
- **🔮 Cast Spell**: Magic and spell casting
- **🎒 Use Item**: Using items from inventory

## Audio Features

### Voice Narration
- AI-generated voice narration for all story segments
- Cached audio files for improved performance
- Adjustable volume controls

### Background Music
- Dynamic music selection based on story context
- Supports multiple audio formats (MP3, WAV, OGG, M4A)
- Music automatically changes for combat vs. exploration
- Place your music files in the `bgm` folder

## API Endpoints

### REST API
- `POST /api/create_game` - Create a new game session
- `GET /api/game/{game_id}/status` - Get game status

### WebSocket
- `ws://localhost:8000/ws/{client_id}` - Real-time game communication

## Project Structure

```
travelerstale/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main server file
│   ├── game_manager.py     # Game logic and state management
│   ├── ai_service.py       # OpenAI integration
│   ├── audio_service.py    # ElevenLabs and audio handling
│   ├── models.py           # Data models
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # Svelte frontend
│   ├── src/
│   │   ├── routes/         # Page routes
│   │   └── lib/            # Components and stores
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Build configuration
└── bgm/                    # Background music files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Troubleshooting

### Common Issues

1. **Pydantic Build Errors**: If you get pydantic-core compilation errors:
   - Try: `python install.py` (uses compatible versions)
   - Or: `pip install fastapi uvicorn openai elevenlabs python-dotenv aiofiles` (minimal install)
   - Python 3.13 may have compatibility issues, try Python 3.10-3.12

2. **API Keys**: Ensure your OpenAI and ElevenLabs API keys are valid and have sufficient credits

3. **Audio Files**: Make sure background music files are in supported formats (MP3, WAV, OGG, M4A)

4. **CORS Issues**: The backend is configured to allow all origins in development

5. **WebSocket Connections**: Check firewall settings if connections fail

6. **Missing Rust/Cargo**: Some Python packages require Rust compiler. Install from https://rustup.rs/

### Getting Help

For support and feature requests, please open an issue on the GitHub repository.

---

**Happy adventuring! 🗡️⚔️🏰**