<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Player } from './stores/gameStore';
	import { gameStore } from './stores/gameStore';
	import GameSettings from './GameSettings.svelte';
	import CharacterSetup from './CharacterSetup.svelte';

	export let players: Player[] = [];
	export let currentPlayer: string = '';
	export let gameStatus: string = 'waiting';
	export let isFirstPlayer: boolean = false;
	export let isGameCreator: boolean = false;
	export let gameTheme: string = '';
	export let gameLanguage: string = 'English';
	export let gmRole: string = '';
	export let chapterLength: string = 'medium';
	export let narratorVoice: string = '';
	export let currentPlayerId: string = '';

	const dispatch = createEventDispatcher();

	let showCharacterSetup = false;

	function startGame() {
		dispatch('start-game', { 
			theme: gameTheme, 
			language: gameLanguage, 
			gmRole: gmRole,
			chapterLength: chapterLength
		});
	}

	function handleSettingsUpdate(event) {
		dispatch('update-settings', event.detail);
	}

	function openCharacterSetup() {
		showCharacterSetup = true;
	}

	function handleSaveCharacters(event) {
		const characters = event.detail.characters;
		
		// Send character updates to server for each character with data
		characters.forEach(char => {
			gameStore.updateCharacter(char.characterName, char.characterDescription, char.characterVoice, char.characterGender);
		});
	}
</script>

<div class="player-list">
	<h3>🧙‍♂️ Players ({players.length}/6)</h3>
	
	<GameSettings 
		isFirstPlayer={isGameCreator}
		{gameStatus}
		{gameTheme}
		{gameLanguage}
		{gmRole}
		{chapterLength}
		{narratorVoice}
		on:update-settings={handleSettingsUpdate}
	/>
	
	<div class="players">
		{#each players as player (player.id)}
			<div class="player" class:active={player.name === currentPlayer}>
				<div class="player-info">
					<div class="player-name">
						{player.name}
						{#if player.name === currentPlayer}
							<span class="turn-indicator">🎯</span>
						{/if}
					</div>
					
					{#if player.character_name}
						<div class="character-name">
							Playing as: {player.character_name}
						</div>
					{/if}
				</div>
				
				<div class="player-status">
					{#if !player.is_active}
						<span class="status-badge inactive">Inactive</span>
					{:else if player.name === currentPlayer}
						<span class="status-badge current">Current Turn</span>
					{:else}
						<span class="status-badge ready">Ready</span>
					{/if}
				</div>
			</div>
		{/each}
		
		{#each Array(6 - players.length) as _, i}
			<div class="player-slot empty">
				<div class="empty-text">Waiting for player...</div>
			</div>
		{/each}
	</div>

	{#if gameStatus === 'waiting' && players.length >= 1}
		<div class="character-setup-section">
			<button on:click={openCharacterSetup} class="character-setup-btn">
				🎭 Setup Characters
			</button>
			<div class="setup-help">
				Define characters before starting the adventure
			</div>
		</div>

		{#if isGameCreator}
			<div class="start-game-section">
				<button on:click={startGame} class="start-game-btn">
					🚀 Start Adventure
				</button>
				<div class="start-help">
					{#if players.length === 1}
						Ready to begin solo adventure!
					{:else}
						{players.length} players ready • Click to start
					{/if}
				</div>
			</div>
		{:else}
			<div class="waiting-for-creator">
				<div class="waiting-message">
					⏳ Waiting for the game creator to start the adventure...
				</div>
			</div>
		{/if}
	{/if}
</div>

<CharacterSetup 
	{players}
	{currentPlayerId}
	{isGameCreator}
	bind:showDialog={showCharacterSetup}
	on:save-characters={handleSaveCharacters}
/>

<style>
	.player-list {
		height: 100%;
	}

	.player-list h3 {
		margin: 0 0 1.5rem 0;
		font-size: 1.4rem;
		text-align: center;
		color: #ffd700;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
	}

	.players {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.player, .player-slot {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 0.8rem;
		padding: 1rem;
		border: 2px solid transparent;
		transition: all 0.3s ease;
	}

	.player.active {
		border-color: #ffd700;
		background: rgba(255, 215, 0, 0.1);
		box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
	}

	.player:hover {
		background: rgba(255, 255, 255, 0.15);
	}

	.player-slot.empty {
		border: 2px dashed rgba(255, 255, 255, 0.3);
		background: rgba(255, 255, 255, 0.05);
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 80px;
	}

	.empty-text {
		color: rgba(255, 255, 255, 0.6);
		font-style: italic;
		text-align: center;
	}

	.player-info {
		margin-bottom: 0.8rem;
	}

	.player-name {
		font-weight: bold;
		font-size: 1.1rem;
		margin-bottom: 0.5rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.turn-indicator {
		animation: pulse 2s infinite;
	}

	.character-name {
		font-size: 0.9rem;
		color: #a0aec0;
		margin-bottom: 0.5rem;
		font-style: italic;
	}

	.player-status {
		display: flex;
		justify-content: center;
	}

	.status-badge {
		padding: 0.3rem 0.8rem;
		border-radius: 1rem;
		font-size: 0.8rem;
		font-weight: bold;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.status-badge.current {
		background: #ffd700;
		color: #1a1a2e;
	}

	.status-badge.ready {
		background: #48bb78;
		color: white;
	}

	.status-badge.inactive {
		background: #718096;
		color: white;
	}

	.character-setup-section {
		margin-top: 1.5rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.05);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 1rem;
		text-align: center;
		backdrop-filter: blur(10px);
	}

	.character-setup-btn {
		width: 100%;
		padding: 0.8rem;
		background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
		color: white;
		border: none;
		border-radius: 0.8rem;
		font-size: 1rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 15px rgba(159, 122, 234, 0.3);
	}

	.character-setup-btn:hover {
		background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(159, 122, 234, 0.4);
	}

	.setup-help {
		margin-top: 0.5rem;
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.7);
		font-style: italic;
	}

	.start-game-section {
		margin-top: 1.5rem;
		padding: 1.5rem;
		background: rgba(255, 215, 0, 0.1);
		border: 2px solid rgba(255, 215, 0, 0.3);
		border-radius: 1rem;
		text-align: center;
		backdrop-filter: blur(10px);
	}

	.start-game-btn {
		width: 100%;
		padding: 1rem;
		background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
		color: #1a1a2e;
		border: none;
		border-radius: 0.8rem;
		font-size: 1.1rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
	}

	.start-game-btn:hover {
		background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
	}

	.start-help {
		margin-top: 0.8rem;
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.8);
		font-style: italic;
	}

	.waiting-for-creator {
		margin-top: 1.5rem;
		padding: 1.5rem;
		background: rgba(255, 255, 255, 0.05);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 1rem;
		text-align: center;
		backdrop-filter: blur(10px);
	}

	.waiting-message {
		color: rgba(255, 255, 255, 0.8);
		font-size: 1rem;
		line-height: 1.4;
	}

	@keyframes pulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.2);
		}
	}

	@media (max-width: 1200px) {
		.players {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
			gap: 1rem;
		}
	}
</style>