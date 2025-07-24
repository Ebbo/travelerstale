<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import GameInterface from '$lib/GameInterface.svelte';
	import { gameStore } from '$lib/stores/gameStore';

	let gameId = '';
	let playerName = '';
	let isConnected = false;
	let showGame = false;

	function createGame() {
		fetch('http://localhost:8000/api/create_game', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		})
		.then(response => response.json())
		.then(data => {
			gameId = data.game_id;
		})
		.catch(error => {
			console.error('Error creating game:', error);
		});
	}

	function joinGame() {
		if (!gameId || !playerName) {
			alert('Please enter both Game ID and Player Name');
			return;
		}

		gameStore.connect(gameId, playerName);
		showGame = true;
	}

	onMount(() => {
		gameStore.subscribe(state => {
			isConnected = state.connected;
		});
	});
</script>

<main class="container">
	{#if !showGame}
		<div class="welcome">
			<h1>🗡️ Traveler's Tale</h1>
			<p class="subtitle">AI-Powered Collaborative Adventure</p>
			
			<div class="game-setup">
				<div class="section">
					<h3>Create New Game</h3>
					<button on:click={createGame} class="btn btn-primary">
						Create Game
					</button>
					{#if gameId}
						<p class="game-id">Game ID: <strong>{gameId}</strong></p>
					{/if}
				</div>

				<div class="divider">OR</div>

				<div class="section">
					<h3>Join Existing Game</h3>
					<input 
						bind:value={gameId} 
						placeholder="Enter Game ID" 
						class="input"
					/>
					<input 
						bind:value={playerName} 
						placeholder="Enter Your Name" 
						class="input"
					/>
					<button 
						on:click={joinGame} 
						class="btn btn-success"
						disabled={!gameId || !playerName}
					>
						Join Game
					</button>
				</div>
			</div>
		</div>
	{:else}
		<GameInterface />
	{/if}
</main>

<style>
	.container {
		width: 100vw;
		height: 100vh;
		margin: 0;
		padding: 1rem;
		font-family: 'Segoe UI', system-ui, sans-serif;
		box-sizing: border-box;
		overflow: hidden;
	}

	.welcome {
		text-align: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 2rem;
		border-radius: 1rem;
		box-shadow: 0 10px 30px rgba(0,0,0,0.3);
		height: calc(100vh - 2rem);
		display: flex;
		flex-direction: column;
		justify-content: center;
		box-sizing: border-box;
	}

	h1 {
		font-size: 3rem;
		margin-bottom: 0.5rem;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
	}

	.subtitle {
		font-size: 1.2rem;
		opacity: 0.9;
		margin-bottom: 2rem;
	}

	.game-setup {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: 2rem;
		align-items: center;
		max-width: 800px;
		margin: 0 auto;
	}

	.section {
		background: rgba(255, 255, 255, 0.1);
		padding: 2rem;
		border-radius: 0.5rem;
		backdrop-filter: blur(10px);
	}

	.section h3 {
		margin-bottom: 1rem;
		font-size: 1.4rem;
	}

	.divider {
		font-weight: bold;
		opacity: 0.7;
		font-size: 1.2rem;
	}

	.input {
		width: 100%;
		padding: 0.75rem;
		margin: 0.5rem 0;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		background: rgba(255, 255, 255, 0.9);
		color: #333;
	}

	.btn {
		width: 100%;
		padding: 1rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		margin: 0.5rem 0;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-primary {
		background: #4CAF50;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: #45a049;
		transform: translateY(-2px);
	}

	.btn-success {
		background: #2196F3;
		color: white;
	}

	.btn-success:hover:not(:disabled) {
		background: #1976D2;
		transform: translateY(-2px);
	}

	.game-id {
		background: rgba(255, 255, 255, 0.2);
		padding: 1rem;
		border-radius: 0.5rem;
		margin-top: 1rem;
		word-break: break-all;
	}

	@media (max-width: 768px) {
		.game-setup {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		
		.divider {
			display: none;
		}
		
		h1 {
			font-size: 2rem;
		}
	}
</style>