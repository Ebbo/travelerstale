import { writable } from 'svelte/store';

export interface Player {
	id: string;
	name: string;
	character_name?: string;
	character_description?: string;
	character_voice?: string;
	character_gender?: string;
	is_active: boolean;
}

export interface ChatMessage {
	player_name: string;
	message: string;
	timestamp: number;
}

export interface GameState {
	connected: boolean;
	gameId: string;
	playerId: string;
	playerName: string;
	players: Player[];
	currentStory: string;
	currentPlayer: string;
	gameStatus: 'waiting' | 'story_telling' | 'gm_working' | 'player_turn' | 'combat' | 'paused';
	storyHistory: Array<{
		text: string;
		voice_file?: string;
		background_music?: string;
	}>;
	chatMessages: ChatMessage[];
	isMyTurn: boolean;
	voiceUrl?: string;
	backgroundMusic?: string;
	isLoading: boolean;
	loadingMessage: string;
	gameTheme: string;
	gameLanguage: string;
	gmRole: string;
	chapterLength: string;
	narratorVoice: string;
	isFirstPlayer: boolean;
	isGameCreator: boolean;
	actionsNeeded: number;
	actionsReceived: number;
	waitingFor: string[];
	hasSubmittedAction: boolean;
}

const initialState: GameState = {
	connected: false,
	gameId: '',
	playerId: '',
	playerName: '',
	players: [],
	currentStory: '',
	currentPlayer: '',
	gameStatus: 'waiting',
	storyHistory: [],
	chatMessages: [],
	isMyTurn: false,
	isLoading: false,
	loadingMessage: '',
	gameTheme: '',
	gameLanguage: 'English',
	gmRole: '',
	chapterLength: 'medium',
	narratorVoice: '',
	isFirstPlayer: false,
	isGameCreator: false,
	actionsNeeded: 0,
	actionsReceived: 0,
	waitingFor: [],
	hasSubmittedAction: false
};

function createGameStore() {
	const { subscribe, set, update } = writable<GameState>(initialState);
	let ws: WebSocket | null = null;

	return {
		subscribe,
		connect: (gameId: string, playerName: string) => {
			const playerId = generatePlayerId();
			const wsUrl = `ws://localhost:8000/ws/${playerId}`;
			
			ws = new WebSocket(wsUrl);
			
			ws.onopen = () => {
				console.log('Connected to game server');
				update(state => ({
					...state,
					connected: true,
					gameId,
					playerId,
					playerName
				}));
				
				// Join the game
				ws?.send(JSON.stringify({
					type: 'join_game',
					game_id: gameId,
					player_name: playerName
				}));
			};
			
			ws.onmessage = (event) => {
				const message = JSON.parse(event.data);
				console.log('Received message:', message);
				
				switch (message.type) {
					case 'player_joined':
						update(state => {
							const allPlayers = message.all_players || [...state.players, message.player];
							const isCreator = message.is_game_creator === true;
							
							console.log('Player joined:', {
								playerId: state.playerId,
								isGameCreator: isCreator,
								messageIsGameCreator: message.is_game_creator,
								allPlayersLength: allPlayers.length,
								joinedPlayerId: message.player?.id
							});
							
							return {
								...state,
								players: allPlayers,
								currentStory: message.current_story || state.currentStory,
								currentPlayer: message.current_player || state.currentPlayer,
								gameStatus: message.game_state,
								isFirstPlayer: allPlayers.length === 1 && allPlayers[0].id === state.playerId,
								isGameCreator: isCreator
							};
						});
						break;
						
					case 'story_update':
						console.log('Story update received:', {
							voice_file: message.voice_file,
							background_music: message.background_music,
							story: message.story?.substring(0, 50) + '...'
						});
						update(state => ({
							...state,
							currentStory: message.story,
							currentPlayer: message.current_player,
							gameStatus: message.game_state,
							storyHistory: [...state.storyHistory, {
								text: message.story,
								voice_file: message.voice_file,
								background_music: message.background_music
							}],
							isMyTurn: true, // All players can act in round-based system
							voiceUrl: message.voice_file ? `http://localhost:8000/${message.voice_file}` : undefined,
							backgroundMusic: message.background_music ? `http://localhost:8000/${message.background_music}` : undefined,
							isLoading: false,
							loadingMessage: '',
							actionsNeeded: message.actions_needed || 0,
							actionsReceived: message.actions_received || 0,
							waitingFor: [],
							hasSubmittedAction: false
						}));
						break;
						
					case 'game_started':
						console.log('Game started message:', {
							current_story: message.current_story?.substring(0, 50) + '...',
							voice_file: message.voice_file,
							background_music: message.background_music
						});
						update(state => ({
							...state,
							currentStory: message.current_story,
							currentPlayer: message.current_player,
							gameStatus: message.game_state,
							isMyTurn: true, // All players can act in round-based system
							voiceUrl: message.voice_file ? `http://localhost:8000/${message.voice_file}` : undefined,
							backgroundMusic: message.background_music ? `http://localhost:8000/${message.background_music}` : undefined,
							isLoading: false,
							loadingMessage: '',
							actionsNeeded: message.actions_needed || 0,
							actionsReceived: message.actions_received || 0,
							waitingFor: [],
							hasSubmittedAction: false
						}));
						break;

					case 'action_received':
						update(state => ({
							...state,
							actionsReceived: message.actions_received,
							actionsNeeded: message.actions_needed,
							waitingFor: message.waiting_for || [],
							chatMessages: [...state.chatMessages, {
								player_name: 'System',
								message: message.message,
								timestamp: Date.now()
							}]
						}));
						break;

					case 'gm_working':
						update(state => ({
							...state,
							gameStatus: 'gm_working',
							isLoading: true,
							loadingMessage: 'The Game Master is processing all actions...',
							actionsReceived: message.actions_received,
							actionsNeeded: message.actions_needed,
							chatMessages: [...state.chatMessages, {
								player_name: 'System',
								message: message.message,
								timestamp: Date.now()
							}]
						}));
						break;

					case 'player_disconnected':
						update(state => ({
							...state,
							players: message.remaining_players,
							currentPlayer: message.current_player || state.currentPlayer,
							chatMessages: [...state.chatMessages, {
								player_name: 'System',
								message: message.message,
								timestamp: Date.now()
							}]
						}));
						break;

					case 'game_ended':
						update(state => ({
							...state,
							chatMessages: [...state.chatMessages, {
								player_name: 'System',
								message: message.message,
								timestamp: Date.now()
							}]
						}));
						// Optionally redirect to home or show game ended screen
						break;

					case 'chat_message':
						update(state => ({
							...state,
							chatMessages: [...state.chatMessages, {
								player_name: message.player_name,
								message: message.message,
								timestamp: message.timestamp
							}]
						}));
						break;

					case 'character_updated':
						update(state => ({
							...state,
							players: message.all_players
						}));
						break;

					case 'error':
						console.error('Game error:', message.message);
						alert(message.message);
						break;
				}
			};
			
			ws.onclose = () => {
				console.log('Disconnected from game server');
				update(state => ({
					...state,
					connected: false
				}));
			};
			
			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
			};
		},
		
		sendAction: (actionType: string, actionText: string) => {
			const state = getCurrentState();
			if (ws && state.connected && state.isMyTurn && !state.hasSubmittedAction) {
				// Mark that this player has submitted an action
				update(state => ({
					...state,
					hasSubmittedAction: true,
					isLoading: state.actionsReceived + 1 >= state.actionsNeeded,
					loadingMessage: state.actionsReceived + 1 >= state.actionsNeeded 
						? 'The Game Master is processing all actions...' 
						: 'Action submitted! Waiting for other players...'
				}));

				ws.send(JSON.stringify({
					type: 'game_action',
					game_id: state.gameId,
					action_type: actionType,
					action_text: actionText
				}));
			}
		},

		sendChatMessage: (message: string) => {
			const state = getCurrentState();
			if (ws && state.connected) {
				ws.send(JSON.stringify({
					type: 'chat_message',
					game_id: state.gameId,
					player_name: state.playerName,
					message: message
				}));
			}
		},

		startGame: (theme?: string, language?: string, gmRole?: string, chapterLength?: string) => {
			const state = getCurrentState();
			if (ws && state.connected && state.isGameCreator) {
				// Set loading state only for the game creator
				update(state => ({
					...state,
					isLoading: true,
					loadingMessage: 'The Game Master is preparing your adventure...'
				}));

				ws.send(JSON.stringify({
					type: 'start_game',
					game_id: state.gameId,
					theme: theme || state.gameTheme,
					language: language || state.gameLanguage,
					gm_role: gmRole || state.gmRole,
					chapter_length: chapterLength || state.chapterLength
				}));
			}
		},

		updateGameSettings: (theme: string, language: string, gmRole?: string, chapterLength?: string) => {
			update(state => ({
				...state,
				gameTheme: theme,
				gameLanguage: language,
				gmRole: gmRole || state.gmRole,
				chapterLength: chapterLength || state.chapterLength
			}));
		},

		updateCharacter: (characterName?: string, characterDescription?: string, characterVoice?: string, characterGender?: string) => {
			const state = getCurrentState();
			if (ws && state.connected) {
				ws.send(JSON.stringify({
					type: 'update_character',
					game_id: state.gameId,
					character_name: characterName,
					character_description: characterDescription,
					character_voice: characterVoice,
					character_gender: characterGender
				}));
			}
		},
		
		disconnect: () => {
			if (ws) {
				ws.close();
				ws = null;
			}
			set(initialState);
		}
	};
	
	function getCurrentState(): GameState {
		let currentState: GameState;
		subscribe(state => {
			currentState = state;
		})();
		return currentState!;
	}
}

function generatePlayerId(): string {
	return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export const gameStore = createGameStore();