<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Player } from './stores/gameStore';

	export let players: Player[] = [];
	export let currentPlayerId: string = '';
	export let isGameCreator: boolean = false;
	export let showDialog: boolean = false;

	const dispatch = createEventDispatcher();

	let characterDescriptions = new Map<string, { name: string; description: string; voice: string; gender: string }>();
	let availableVoices: any[] = [];
	let voicesLoaded = false;

	// Initialize character descriptions for all players
	$: if (players.length > 0) {
		players.forEach(player => {
			if (!characterDescriptions.has(player.id)) {
				characterDescriptions.set(player.id, {
					name: player.character_name || '',
					description: player.character_description || '',
					voice: player.character_voice || '',
					gender: player.character_gender || ''
				});
			} else {
				// Update existing data if player data changed
				const existing = characterDescriptions.get(player.id);
				if (existing) {
					existing.name = player.character_name || existing.name;
					existing.description = player.character_description || existing.description;
					existing.voice = player.character_voice || existing.voice;
					existing.gender = player.character_gender || existing.gender;
					characterDescriptions.set(player.id, existing);
				}
			}
		});
		characterDescriptions = characterDescriptions; // Trigger reactivity
	}

	// Load available voices when dialog opens
	$: if (showDialog && !voicesLoaded) {
		loadVoices();
	}

	async function loadVoices() {
		try {
			const response = await fetch('http://localhost:8000/api/voices');
			const data = await response.json();
			if (data.type === 'voices_list') {
				availableVoices = data.voices;
				voicesLoaded = true;
			}
		} catch (error) {
			console.error('Failed to load voices:', error);
			// Fallback to basic voices if API fails
			availableVoices = [
				{id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel', gender: 'female', category: 'heroic', description: 'Clear, confident narrator'},
				{id: 'EXAVITQu4vr4xnSDxMaL', name: 'Adam', gender: 'male', category: 'heroic', description: 'Deep, confident male voice'}
			];
			voicesLoaded = true;
		}
	}

	function updateCharacter(playerId: string, field: 'name' | 'description' | 'voice' | 'gender', value: string) {
		const current = characterDescriptions.get(playerId) || { name: '', description: '', voice: '', gender: '' };
		current[field] = value;
		characterDescriptions.set(playerId, current);
		characterDescriptions = characterDescriptions; // Trigger reactivity
	}

	function saveCharacters() {
		// Only save the current player's character
		const charData = characterDescriptions.get(currentPlayerId);
		if (charData) {
			const characterData = [{
				playerId: currentPlayerId,
				characterName: charData.name.trim() || null,
				characterDescription: charData.description.trim(),
				characterVoice: charData.voice || null,
				characterGender: charData.gender || null
			}];
			
			dispatch('save-characters', { characters: characterData });
		}
		showDialog = false;
	}

	function closeDialog() {
		showDialog = false;
	}
</script>

{#if showDialog}
	<div class="modal-overlay" on:click={closeDialog} on:keydown>
		<div class="modal-content" on:click|stopPropagation on:keydown>
			<div class="modal-header">
				<h2>🎭 Your Character Setup</h2>
				<p class="modal-subtitle">
					Set up your character details. This helps the Game Master understand your character's background, abilities, and voice.
				</p>
			</div>

			<div class="character-form-container">
				{#if players.length > 0}
					{@const currentPlayer = players.find(p => p.id === currentPlayerId)}
					{#if currentPlayer}
						{@const charData = characterDescriptions.get(currentPlayer.id) || { name: '', description: '', voice: '', gender: '' }}
					
					<div class="character-card">
						<div class="player-header">
							<h3>👤 {currentPlayer.name}</h3>
							<p class="player-subtitle">Customize your character for this adventure</p>
						</div>
						
						<div class="character-form">
							<div class="form-group">
								<label for="char-name">Character Name (optional)</label>
								<input
									id="char-name"
									type="text"
									bind:value={charData.name}
									on:input={(e) => updateCharacter(currentPlayer.id, 'name', e.target.value)}
									placeholder="e.g., Gandalf the Grey, Aria Moonwhisper..."
									class="character-input"
								/>
							</div>
							
							<div class="form-group">
								<label for="char-gender">Character Gender</label>
								<div class="gender-buttons">
									<button
										type="button"
										class="gender-btn {charData.gender === 'male' ? 'active' : ''}"
										on:click={() => updateCharacter(currentPlayer.id, 'gender', 'male')}
									>
										👨 Male
									</button>
									<button
										type="button"
										class="gender-btn {charData.gender === 'female' ? 'active' : ''}"
										on:click={() => updateCharacter(currentPlayer.id, 'gender', 'female')}
									>
										👩 Female
									</button>
								</div>
								<p class="gender-help">This helps with pronouns and voice recommendations</p>
							</div>
							
							<div class="form-group">
								<label for="char-description">Character Description</label>
								<textarea
									id="char-description"
									bind:value={charData.description}
									on:input={(e) => updateCharacter(currentPlayer.id, 'description', e.target.value)}
									placeholder="Describe your character's background, skills, personality, or special abilities... e.g., 'A cunning rogue with expertise in stealth and lockpicking, quick-witted but sometimes too curious for their own good.'"
									class="character-textarea"
									rows="4"
								></textarea>
								<p class="description-help">The Game Master will use this to make the story more engaging and relevant to your character</p>
							</div>
							
							<div class="form-group">
								<label for="char-voice">Character Voice {charData.gender ? `(${charData.gender} voices highlighted)` : ''}</label>
								{#if voicesLoaded}
									<select
										id="char-voice"
										bind:value={charData.voice}
										on:change={(e) => updateCharacter(currentPlayer.id, 'voice', e.target.value)}
										class="character-select"
									>
										<option value="">🔇 No voice selected</option>
										<optgroup label="🦸 Male - Heroic">
											{#each availableVoices.filter(v => v.gender === 'male' && v.category === 'heroic') as voice}
												<option value={voice.id}>
													🎭 {voice.name} - {voice.description}
												</option>
											{/each}
										</optgroup>
										<optgroup label="🤪 Male - Quirky">
											{#each availableVoices.filter(v => v.gender === 'male' && v.category === 'quirky') as voice}
												<option value={voice.id}>
													🎭 {voice.name} - {voice.description}
												</option>
											{/each}
										</optgroup>
										<optgroup label="👸 Female - Heroic">
											{#each availableVoices.filter(v => v.gender === 'female' && v.category === 'heroic') as voice}
												<option value={voice.id}>
													🎭 {voice.name} - {voice.description}
												</option>
											{/each}
										</optgroup>
										<optgroup label="🎪 Female - Quirky">
											{#each availableVoices.filter(v => v.gender === 'female' && v.category === 'quirky') as voice}
												<option value={voice.id}>
													🎭 {voice.name} - {voice.description}
												</option>
											{/each}
										</optgroup>
										<optgroup label="✨ Special Characters">
											{#each availableVoices.filter(v => v.category === 'mystical' || v.category === 'villain' || v.category === 'character') as voice}
												<option value={voice.id}>
													🎭 {voice.name} - {voice.description}
												</option>
											{/each}
										</optgroup>
									</select>
									{#if charData.voice}
										{@const selectedVoice = availableVoices.find(v => v.id === charData.voice)}
										{#if selectedVoice}
											<div class="voice-preview">
												🎯 Selected: <strong>{selectedVoice.name}</strong> - {selectedVoice.description}
											</div>
										{/if}
									{/if}
								{:else}
									<div class="character-display">🔄 Loading available voices...</div>
								{/if}
							</div>
							
							<div class="form-group">
								<label for="char-desc">Character Description</label>
								<textarea
									id="char-desc"
									bind:value={charData.description}
									on:input={(e) => updateCharacter(currentPlayer.id, 'description', e.target.value)}
									placeholder="Describe your character's appearance, abilities, background, and personality. For example: 'A wise elven mage with silver hair and emerald eyes. Known for her quick wit and mastery of nature magic. Has a mysterious past and speaks with ancient wisdom...'"
									rows="6"
									class="character-textarea"
								></textarea>
								<div class="char-count">
									{charData.description.length} characters
								</div>
							</div>
						</div>
					</div>
					{:else}
						<div class="character-card">
							<div class="error-message">
								❌ Unable to load your character data. Please try refreshing the page.
							</div>
						</div>
					{/if}
				{:else}
					<div class="character-card">
						<div class="error-message">
							🔄 Loading player data...
						</div>
					</div>
				{/if}
			</div>

			<div class="modal-actions">
				<button on:click={closeDialog} class="btn btn-secondary">
					❌ Cancel
				</button>
				<button on:click={saveCharacters} class="btn btn-primary">
					💾 Save Character
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(5px);
	}

	.modal-content {
		background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
		border-radius: 1rem;
		padding: 2rem;
		width: 90%;
		max-width: 800px;
		max-height: 90vh;
		overflow-y: auto;
		border: 2px solid rgba(255, 255, 255, 0.1);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
	}

	.modal-header {
		text-align: center;
		margin-bottom: 2rem;
		border-bottom: 2px solid rgba(255, 255, 255, 0.1);
		padding-bottom: 1.5rem;
	}

	.modal-header h2 {
		margin: 0 0 1rem 0;
		font-size: 1.8rem;
		color: #ffd700;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
	}

	.modal-subtitle {
		margin: 0;
		color: rgba(255, 255, 255, 0.8);
		line-height: 1.5;
	}

	.character-form-container {
		margin-bottom: 2rem;
	}

	.character-card {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 0.8rem;
		padding: 1.5rem;
		border: 2px solid rgba(255, 255, 255, 0.1);
	}

	.character-card.readonly {
		background: rgba(255, 255, 255, 0.02);
		border-color: rgba(255, 255, 255, 0.05);
		opacity: 0.8;
	}

	.player-header {
		margin-bottom: 1rem;
		text-align: center;
	}

	.player-header h3 {
		margin: 0;
		color: #ffd700;
		font-size: 1.2rem;
	}

	.player-subtitle {
		margin: 0.5rem 0 0 0;
		color: rgba(255, 255, 255, 0.7);
		font-size: 0.9rem;
		font-style: italic;
	}

	.voice-preview {
		margin-top: 0.5rem;
		padding: 0.5rem;
		background: rgba(255, 215, 0, 0.1);
		border: 1px solid rgba(255, 215, 0, 0.3);
		border-radius: 0.5rem;
		font-size: 0.85rem;
		color: #ffd700;
	}

	.char-count {
		text-align: right;
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
		margin-top: 0.25rem;
	}

	.error-message {
		text-align: center;
		color: #f56565;
		font-size: 1rem;
		padding: 2rem;
	}

	.character-select optgroup {
		background: #2d3748;
		color: white;
		font-weight: bold;
		padding: 0.5rem;
	}

	.gender-buttons {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.gender-btn {
		flex: 1;
		padding: 0.8rem 1rem;
		background: rgba(255, 255, 255, 0.1);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.5rem;
		color: white;
		font-size: 0.9rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.gender-btn:hover {
		background: rgba(255, 255, 255, 0.15);
		border-color: rgba(255, 215, 0, 0.3);
	}

	.gender-btn.active {
		background: rgba(255, 215, 0, 0.2);
		border-color: #ffd700;
		color: #ffd700;
		box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
	}

	.gender-help,
	.description-help {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.6);
		margin-top: 0.5rem;
		font-style: italic;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: bold;
		color: white;
		font-size: 0.9rem;
	}

	.character-input,
	.character-textarea,
	.character-select {
		width: 100%;
		padding: 0.8rem;
		background: rgba(255, 255, 255, 0.1);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.5rem;
		color: white;
		font-size: 0.9rem;
		font-family: inherit;
		transition: all 0.3s ease;
		box-sizing: border-box;
	}

	.character-input:focus,
	.character-textarea:focus,
	.character-select:focus {
		outline: none;
		border-color: #ffd700;
		box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
	}

	.character-select option {
		background: #2d3748;
		color: white;
		padding: 0.5rem;
	}

	.character-textarea {
		resize: vertical;
		min-height: 100px;
	}

	.character-input::placeholder,
	.character-textarea::placeholder {
		color: rgba(255, 255, 255, 0.5);
		font-style: italic;
	}

	.character-display {
		padding: 0.8rem;
		background: rgba(255, 255, 255, 0.05);
		border: 2px solid rgba(255, 255, 255, 0.1);
		border-radius: 0.5rem;
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.9rem;
		min-height: 1.2rem;
	}

	.character-display.description {
		min-height: 100px;
		line-height: 1.4;
		white-space: pre-wrap;
	}

	.modal-actions {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		padding-top: 1.5rem;
		border-top: 2px solid rgba(255, 255, 255, 0.1);
	}

	.btn {
		padding: 0.8rem 1.5rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.btn-secondary {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		border: 2px solid rgba(255, 255, 255, 0.2);
	}

	.btn-secondary:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	.btn-primary {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.btn-primary:hover {
		background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
		transform: translateY(-1px);
		box-shadow: 0 5px 15px rgba(0,0,0,0.3);
	}

	@media (max-width: 768px) {
		.modal-content {
			width: 95%;
			padding: 1.5rem;
		}

		.modal-actions {
			flex-direction: column;
		}

		.btn {
			width: 100%;
		}
		
		.character-textarea {
			rows: 4;
		}
	}
</style>