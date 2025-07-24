<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { gameStore, type GameState } from './stores/gameStore';
	import PlayerList from './PlayerList.svelte';
	import StoryDisplay from './StoryDisplay.svelte';
	import ActionInput from './ActionInput.svelte';
	import AudioPlayer from './AudioPlayer.svelte';
	import ChatWindow from './ChatWindow.svelte';
	import LoadingOverlay from './LoadingOverlay.svelte';

	let gameState: GameState;
	let unsubscribe: () => void;
	let chatHeight = 60; // Percentage of right panel height for chat
	let isResizing = false;

	onMount(() => {
		unsubscribe = gameStore.subscribe(state => {
			gameState = state;
		});
	});

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
		}
	});

	function leaveGame() {
		gameStore.disconnect();
		window.location.reload();
	}

	async function copyGameId(gameId: string) {
		try {
			await navigator.clipboard.writeText(gameId);
			// Could add a toast notification here
		} catch (err) {
			console.error('Failed to copy game ID:', err);
		}
	}

	function handleResizeStart(event: MouseEvent) {
		isResizing = true;
		event.preventDefault();
		
		const isMobile = window.innerWidth <= 1200;
		
		function handleMouseMove(e: MouseEvent) {
			if (!isResizing) return;
			
			const rightPanel = document.querySelector('.right-panel') as HTMLElement;
			if (!rightPanel) return;
			
			const rect = rightPanel.getBoundingClientRect();
			
			if (isMobile) {
				// Horizontal resizing for mobile
				const relativeX = e.clientX - rect.left;
				const percentage = Math.max(30, Math.min(80, (relativeX / rect.width) * 100));
				chatHeight = percentage;
			} else {
				// Vertical resizing for desktop
				const relativeY = e.clientY - rect.top;
				const percentage = Math.max(30, Math.min(80, (relativeY / rect.height) * 100));
				chatHeight = percentage;
			}
		}
		
		function handleMouseUp() {
			isResizing = false;
			document.removeEventListener('mousemove', handleMouseMove);
			document.removeEventListener('mouseup', handleMouseUp);
		}
		
		document.addEventListener('mousemove', handleMouseMove);
		document.addEventListener('mouseup', handleMouseUp);
	}
</script>

<div class="game-container">
	{#if gameState}
		<header class="game-header">
			<div class="header-content">
				<h2>🗡️ Traveler's Tale</h2>
				<div class="game-info">
					<div class="game-id-container">
						<span class="game-id">Game: {gameState.gameId}</span>
						<button on:click={() => copyGameId(gameState.gameId)} class="btn btn-copy">📋</button>
					</div>
					<span class="status">Status: {gameState.gameStatus.replace('_', ' ')}</span>
					<button on:click={leaveGame} class="btn btn-danger">Leave Game</button>
				</div>
			</div>
		</header>

		<main class="game-main">
			<div class="left-panel">
				<PlayerList 
					players={gameState.players} 
					currentPlayer={gameState.currentPlayer}
					gameStatus={gameState.gameStatus}
					isFirstPlayer={gameState.isFirstPlayer}
					isGameCreator={gameState.isGameCreator}
					gameTheme={gameState.gameTheme}
					gameLanguage={gameState.gameLanguage}
					gmRole={gameState.gmRole}
					chapterLength={gameState.chapterLength}
					narratorVoice={gameState.narratorVoice}
					currentPlayerId={gameState.playerId}
					on:start-game={(event) => gameStore.startGame(event.detail.theme, event.detail.language, event.detail.gmRole, event.detail.chapterLength, event.detail.narratorVoice)}
					on:update-settings={(event) => gameStore.updateGameSettings(event.detail.theme, event.detail.language, event.detail.gmRole, event.detail.chapterLength, event.detail.narratorVoice)}
				/>
			</div>

			<div class="center-panel">
				<StoryDisplay 
					story={gameState.currentStory} 
					storyHistory={gameState.storyHistory}
				/>
				
				{#if gameState.gameStatus === 'player_turn' || gameState.gameStatus === 'combat'}
					<ActionInput 
						isMyTurn={gameState.isMyTurn} 
						currentPlayer={gameState.currentPlayer}
						gameStatus={gameState.gameStatus}
						actionsNeeded={gameState.actionsNeeded}
						actionsReceived={gameState.actionsReceived}
						waitingFor={gameState.waitingFor}
						hasSubmittedAction={gameState.hasSubmittedAction}
						on:action={(event) => gameStore.sendAction(event.detail.type, event.detail.text)}
					/>
				{/if}
			</div>

			<div class="right-panel" class:resizing={isResizing} style="--chat-width: {chatHeight}%;">
				<div class="right-panel-top" style="height: {chatHeight}%;">
					<ChatWindow 
						messages={gameState.chatMessages}
						playerName={gameState.playerName}
						gameId={gameState.gameId}
						on:chat={(event) => gameStore.sendChatMessage(event.detail.message)}
					/>
				</div>
				
				<div class="resize-handle" on:mousedown={handleResizeStart}>
					<div class="resize-line"></div>
					<div class="resize-icon">
						<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
							<path d="M2 4h12v1H2V4zm0 3h12v1H2V7zm0 3h12v1H2v-1z"/>
						</svg>
					</div>
				</div>
				
				<div class="right-panel-bottom" style="height: {100 - chatHeight}%;">
					<AudioPlayer 
						voiceUrl={gameState.voiceUrl}
						backgroundMusic={gameState.backgroundMusic}
					/>
				</div>
			</div>
		</main>
	{/if}

	<LoadingOverlay 
		isVisible={gameState?.isLoading || false}
		message={gameState?.loadingMessage || 'Loading...'}
	/>
</div>

<style>
	.game-container {
		width: 100vw;
		height: 100vh;
		background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
		color: white;
		font-family: 'Segoe UI', system-ui, sans-serif;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.game-header {
		background: rgba(0, 0, 0, 0.3);
		border-bottom: 2px solid #4a5568;
		padding: 1rem 0;
		flex-shrink: 0;
	}

	.header-content {
		width: 100%;
		padding: 0 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-sizing: border-box;
	}

	.header-content h2 {
		margin: 0;
		font-size: 1.8rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
	}

	.game-info {
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	.game-id-container {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: rgba(255, 255, 255, 0.1);
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		backdrop-filter: blur(10px);
	}

	.game-id {
		font-size: 0.9rem;
		margin: 0;
	}

	.status {
		background: rgba(255, 255, 255, 0.1);
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.9rem;
		backdrop-filter: blur(10px);
	}

	.game-main {
		flex: 1;
		display: grid;
		grid-template-columns: 320px 1fr 380px;
		gap: 1rem;
		padding: 1rem;
		min-height: 0;
		box-sizing: border-box;
		overflow: hidden;
	}

	.left-panel {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 1rem;
		padding: 1rem;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow-y: auto;
	}

	.right-panel {
		display: flex;
		flex-direction: column;
		min-height: 0;
		height: 100%;
		position: relative;
	}

	.right-panel-top {
		min-height: 0;
		overflow: hidden;
		margin-bottom: 0.5rem;
	}

	.resize-handle {
		height: 8px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 4px;
		cursor: ns-resize;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		margin: 0.5rem 0;
		transition: background 0.2s ease;
		user-select: none;
	}

	.resize-handle:hover {
		background: rgba(255, 215, 0, 0.3);
	}

	.resize-line {
		width: 100%;
		height: 2px;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 1px;
		position: absolute;
	}

	.resize-icon {
		color: rgba(255, 255, 255, 0.6);
		background: rgba(0, 0, 0, 0.5);
		padding: 0.4rem;
		border-radius: 0.3rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.resize-icon svg {
		width: 16px;
		height: 16px;
		transition: transform 0.2s ease;
	}

	.resize-handle:hover .resize-icon {
		color: #ffd700;
	}

	.right-panel.resizing {
		user-select: none;
	}

	.right-panel.resizing .resize-handle {
		background: rgba(255, 215, 0, 0.5);
	}

	.right-panel-bottom {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 1rem;
		padding: 0.8rem;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow-y: auto;
		margin-top: 0.5rem;
		min-height: 150px;
	}

	.center-panel {
		background: rgba(255, 255, 255, 0.08);
		border-radius: 1rem;
		padding: 1.5rem;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		display: flex;
		flex-direction: column;
		gap: 1rem;
		min-height: 0;
		overflow: hidden;
	}

	.btn {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 0.9rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.btn-danger {
		background: #e53e3e;
		color: white;
	}

	.btn-danger:hover {
		background: #c53030;
		transform: translateY(-1px);
	}

	.btn-copy {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		padding: 0.3rem 0.5rem;
		font-size: 0.8rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.btn-copy:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	@media (max-width: 1600px) {
		.game-main {
			grid-template-columns: 300px 1fr 360px;
		}
	}

	@media (max-width: 1400px) {
		.game-main {
			grid-template-columns: 280px 1fr 320px;
		}
	}

	@media (max-width: 1200px) {
		.game-main {
			grid-template-columns: 1fr;
			gap: 1rem;
			overflow-y: auto;
			padding: 0.5rem;
		}

		.left-panel, .right-panel {
			min-height: 400px;
		}

		.right-panel {
			order: 3;
			flex-direction: row;
			height: auto;
		}

		.right-panel-top {
			width: var(--chat-width, 60%);
			height: 400px !important;
			margin: 0;
		}

		.right-panel-bottom {
			width: calc(100% - var(--chat-width, 60%));
			height: 400px !important;
			margin: 0;
		}

		.resize-handle {
			width: 8px;
			height: auto;
			cursor: ew-resize;
			margin: 0 0.5rem;
		}

		.resize-line {
			width: 2px;
			height: 100%;
		}

		.resize-icon svg {
			transform: rotate(90deg);
		}

		.center-panel {
			order: 2;
			min-height: 500px;
		}

		.left-panel {
			order: 1;
		}

		.header-content {
			flex-direction: column;
			gap: 1rem;
		}

		.game-info {
			flex-wrap: wrap;
			justify-content: center;
		}
	}

	@media (max-width: 900px) {
		.game-main {
			grid-template-columns: 1fr;
			padding: 0.5rem;
		}

		.left-panel, .right-panel {
			min-height: 350px;
		}

		.center-panel {
			min-height: 450px;
		}
	}

	@media (max-width: 768px) {
		.game-main {
			padding: 0.5rem;
		}

		.center-panel, .left-panel {
			padding: 1rem;
		}

		.right-panel-bottom {
			padding: 1rem;
		}

		.header-content {
			padding: 0 1rem;
		}
	}
</style>