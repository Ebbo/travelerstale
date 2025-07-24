<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let isFirstPlayer: boolean = false;
	export let gameStatus: string = 'waiting';
	export let gameTheme: string = '';
	export let gameLanguage: string = 'English';
	export let gmRole: string = '';
	export let chapterLength: string = 'medium';
	export let narratorVoice: string = '';

	const dispatch = createEventDispatcher();

	let localTheme = gameTheme;
	let localLanguage = gameLanguage;
	let localGmRole = gmRole;
	let localChapterLength = chapterLength;

	const languages = [
		'English', 'Spanish', 'French', 'German', 'Italian', 
		'Portuguese', 'Russian', 'Japanese', 'Korean', 'Chinese'
	];

	const themeExamples = [
		'Epic fantasy adventure',
		'Sci-fi space exploration', 
		'Mystery detective story',
		'Horror survival',
		'Medieval kingdom',
		'Cyberpunk dystopia',
		'Pirate adventure',
		'Wild west',
		'Zombie apocalypse',
		'Time travel adventure'
	];

	const gmRoleExamples = [
		'Mysterious and atmospheric narrator who loves building suspense',
		'Enthusiastic storyteller who encourages creative solutions',
		'Tactical military commander who focuses on strategic challenges',
		'Whimsical fairy tale narrator with a playful tone',
		'Dark and gritty narrator who emphasizes consequences',
		'Scholarly historian who provides rich world details'
	];

	function updateSettings() {
		dispatch('update-settings', {
			theme: localTheme,
			language: localLanguage,
			gmRole: localGmRole,
			chapterLength: localChapterLength
		});
	}

	$: if (localTheme !== gameTheme || localLanguage !== gameLanguage || localGmRole !== gmRole || localChapterLength !== chapterLength) {
		updateSettings();
	}
</script>

{#if isFirstPlayer && gameStatus === 'waiting'}
	<div class="game-settings">
		<h4>🎮 Game Settings</h4>
		<div class="settings-section">
			<label for="language">🌍 Language:</label>
			<select id="language" bind:value={localLanguage} class="setting-select">
				{#each languages as lang}
					<option value={lang}>{lang}</option>
				{/each}
			</select>
		</div>

		<div class="settings-section">
			<label for="chapterLength">📖 Chapter Length:</label>
			<select id="chapterLength" bind:value={localChapterLength} class="setting-select">
				<option value="short">⚡ Short - Quick, action-packed scenes (1-2 paragraphs)</option>
				<option value="medium">⚖️ Medium - Balanced pacing and detail (2-3 paragraphs)</option>
				<option value="long">📚 Long - Rich, immersive storytelling (3-4 paragraphs)</option>
			</select>
		</div>

		<div class="settings-section">
			<div class="narrator-info">
				<label>🎙️ Narrator Voice:</label>
				<div class="fixed-narrator">
					<span class="narrator-name">🎭 Freya</span>
					<span class="narrator-description">Young, energetic narrator - perfect for all languages</span>
				</div>
			</div>
		</div>

		<div class="settings-section">
			<label for="theme">Adventure Theme (Optional):</label>
			<input 
				id="theme"
				type="text" 
				bind:value={localTheme}
				placeholder="e.g., Epic fantasy quest, Space exploration..."
				maxlength="100"
				class="setting-input"
			/>
			<div class="theme-examples">
				<span class="examples-label">Ideas:</span>
				{#each themeExamples.slice(0, 3) as example, i}
					<button 
						type="button" 
						on:click={() => localTheme = example}
						class="example-btn"
					>
						{example}
					</button>
				{/each}
			</div>
		</div>

		<div class="settings-section">
			<label for="gmRole">Game Master Personality (Optional):</label>
			<textarea 
				id="gmRole"
				bind:value={localGmRole}
				placeholder="e.g., Enthusiastic storyteller who loves epic adventures and encourages creative solutions..."
				maxlength="200"
				rows="3"
				class="setting-textarea"
			></textarea>
			<div class="gm-examples">
				<span class="examples-label">Personality styles:</span>
				{#each gmRoleExamples.slice(0, 2) as example, i}
					<button 
						type="button" 
						on:click={() => localGmRole = example}
						class="example-btn"
					>
						{example}
					</button>
				{/each}
			</div>
		</div>

		<div class="settings-info">
			<div class="info-item">
				👑 <strong>Game Master</strong> - You control the game settings
			</div>
			<div class="info-item">
				🎭 <strong>Theme</strong> - Guide the AI's story generation
			</div>
			<div class="info-item">
				🎪 <strong>Personality</strong> - Define the AI narrator's style and tone
			</div>
		</div>
	</div>
{/if}

<style>
	.game-settings {
		background: rgba(255, 215, 0, 0.1);
		border: 2px solid rgba(255, 215, 0, 0.3);
		border-radius: 1rem;
		padding: 1.5rem;
		margin-bottom: 1rem;
		backdrop-filter: blur(10px);
	}

	.game-settings h4 {
		margin: 0 0 1rem 0;
		color: #ffd700;
		font-size: 1.2rem;
		text-align: center;
	}

	.settings-section {
		margin-bottom: 1.5rem;
	}

	.settings-section label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: bold;
		color: white;
		font-size: 0.9rem;
	}

	.setting-select, .setting-input, .setting-textarea {
		width: 100%;
		padding: 0.8rem;
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.5rem;
		background: rgba(255, 255, 255, 0.1);
		color: white;
		font-size: 0.9rem;
		font-family: inherit;
		transition: all 0.3s ease;
	}

	.setting-textarea {
		resize: vertical;
		min-height: 80px;
		line-height: 1.4;
	}

	.setting-select:focus, .setting-input:focus, .setting-textarea:focus {
		outline: none;
		border-color: #ffd700;
		box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
	}

	.setting-select option {
		background: #2a2a40;
		color: white;
	}

	.setting-input::placeholder, .setting-textarea::placeholder {
		color: rgba(255, 255, 255, 0.5);
	}

	.theme-examples, .gm-examples {
		margin-top: 0.8rem;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		align-items: center;
	}

	.examples-label {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.7);
		margin-right: 0.5rem;
	}

	.example-btn {
		padding: 0.3rem 0.6rem;
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.3rem;
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.example-btn:hover {
		background: rgba(255, 215, 0, 0.2);
		border-color: rgba(255, 215, 0, 0.5);
		color: white;
	}

	.settings-info {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.5rem;
		padding: 1rem;
		margin-top: 1rem;
	}

	.info-item {
		font-size: 0.85rem;
		color: rgba(255, 255, 255, 0.8);
		margin-bottom: 0.5rem;
		line-height: 1.4;
	}

	.info-item:last-child {
		margin-bottom: 0;
	}

	.info-item strong {
		color: #ffd700;
	}

	.narrator-info {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.fixed-narrator {
		padding: 0.8rem;
		background: rgba(255, 215, 0, 0.1);
		border: 2px solid rgba(255, 215, 0, 0.3);
		border-radius: 0.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.narrator-name {
		font-weight: bold;
		color: #ffd700;
		font-size: 1rem;
	}

	.narrator-description {
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.85rem;
		font-style: italic;
	}

	@media (max-width: 768px) {
		.game-settings {
			padding: 1rem;
		}

		.theme-examples {
			flex-direction: column;
			align-items: stretch;
		}

		.examples-label {
			margin-bottom: 0.5rem;
		}

		.example-btn {
			font-size: 0.8rem;
			padding: 0.5rem;
		}
	}
</style>