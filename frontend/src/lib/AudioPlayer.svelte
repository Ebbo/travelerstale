<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let voiceUrl: string | undefined = undefined;
	export let backgroundMusic: string | undefined = undefined;

	let voiceAudio: HTMLAudioElement;
	let bgmAudio: HTMLAudioElement;
	let isVoicePlaying = false;
	let isBgmPlaying = false;
	let bgmVolume = 0.3;
	let voiceVolume = 0.8;
	let currentVoiceUrl = '';
	let currentBgmUrl = '';

	onMount(() => {
		// Initialize audio elements
		voiceAudio = new Audio();
		bgmAudio = new Audio();
		
		// Set up event listeners
		voiceAudio.addEventListener('play', () => isVoicePlaying = true);
		voiceAudio.addEventListener('pause', () => isVoicePlaying = false);
		voiceAudio.addEventListener('ended', () => isVoicePlaying = false);
		
		bgmAudio.addEventListener('play', () => isBgmPlaying = true);
		bgmAudio.addEventListener('pause', () => isBgmPlaying = false);
		bgmAudio.addEventListener('ended', () => isBgmPlaying = false);
		
		// Set initial volumes
		bgmAudio.volume = bgmVolume;
		voiceAudio.volume = voiceVolume;
		bgmAudio.loop = true;
	});

	onDestroy(() => {
		if (voiceAudio) {
			voiceAudio.pause();
		}
		if (bgmAudio) {
			bgmAudio.pause();
		}
	});

	// React to voice URL changes
	$: if (voiceUrl && voiceUrl !== currentVoiceUrl) {
		console.log('New voice URL received:', voiceUrl);
		currentVoiceUrl = voiceUrl;
		playVoice();
	}

	// React to background music URL changes  
	$: if (backgroundMusic && backgroundMusic !== currentBgmUrl) {
		currentBgmUrl = backgroundMusic;
		playBackgroundMusic();
	}

	// Update volumes when sliders change
	$: if (bgmAudio) bgmAudio.volume = bgmVolume;
	$: if (voiceAudio) voiceAudio.volume = voiceVolume;

	async function playVoice() {
		if (!voiceAudio || !voiceUrl) return;
		
		try {
			// Lower background music volume for voice
			if (bgmAudio && isBgmPlaying) {
				bgmAudio.volume = bgmVolume * 0.3;
			}
			
			voiceAudio.src = voiceUrl;
			await voiceAudio.play();
			
			// Restore background music volume when voice ends
			voiceAudio.addEventListener('ended', () => {
				if (bgmAudio && isBgmPlaying) {
					bgmAudio.volume = bgmVolume;
				}
			}, { once: true });
			
		} catch (error) {
			console.error('Error playing voice:', error);
		}
	}

	async function playBackgroundMusic() {
		if (!bgmAudio || !backgroundMusic) return;
		
		try {
			bgmAudio.src = backgroundMusic;
			await bgmAudio.play();
		} catch (error) {
			console.error('Error playing background music:', error);
		}
	}

	function toggleVoice() {
		if (!voiceAudio) return;
		
		if (isVoicePlaying) {
			voiceAudio.pause();
		} else if (currentVoiceUrl) {
			playVoice();
		}
	}

	function toggleBackgroundMusic() {
		if (!bgmAudio) return;
		
		if (isBgmPlaying) {
			bgmAudio.pause();
		} else if (currentBgmUrl) {
			playBackgroundMusic();
		}
	}

	function stopAll() {
		if (voiceAudio) voiceAudio.pause();
		if (bgmAudio) bgmAudio.pause();
	}
</script>

<div class="audio-player">
	<h3>🔊 Audio Controls</h3>
	
	<div class="audio-section">
		<div class="section-header">
			<h4>🎵 Background Music</h4>
			<button 
				on:click={toggleBackgroundMusic}
				class="btn btn-small"
				class:btn-playing={isBgmPlaying}
				disabled={!currentBgmUrl}
			>
				{isBgmPlaying ? '⏸️ Pause' : '▶️ Play'}
			</button>
		</div>
		
		<div class="volume-control">
			<label>Volume:</label>
			<input 
				type="range" 
				min="0" 
				max="1" 
				step="0.1" 
				bind:value={bgmVolume}
				class="volume-slider"
			/>
			<span class="volume-display">{Math.round(bgmVolume * 100)}%</span>
		</div>
		
		{#if currentBgmUrl}
			<div class="track-info">
				<div class="track-name">🎼 Currently playing ambient music</div>
				{#if isBgmPlaying}
					<div class="equalizer">
						<div class="bar"></div>
						<div class="bar"></div>
						<div class="bar"></div>
						<div class="bar"></div>
					</div>
				{/if}
			</div>
		{:else}
			<div class="no-track">No background music selected</div>
		{/if}
	</div>

	<div class="audio-section">
		<div class="section-header">
			<h4>🗣️ Voice Narration</h4>
			<button 
				on:click={toggleVoice}
				class="btn btn-small"
				class:btn-playing={isVoicePlaying}
				disabled={!currentVoiceUrl}
			>
				{isVoicePlaying ? '⏸️ Pause' : '▶️ Play'}
			</button>
		</div>
		
		<div class="volume-control">
			<label>Volume:</label>
			<input 
				type="range" 
				min="0" 
				max="1" 
				step="0.1" 
				bind:value={voiceVolume}
				class="volume-slider"
			/>
			<span class="volume-display">{Math.round(voiceVolume * 100)}%</span>
		</div>
		
		{#if currentVoiceUrl}
			<div class="track-info">
				<div class="track-name">🎙️ AI Narrator Voice</div>
				{#if isVoicePlaying}
					<div class="voice-indicator">
						<span class="speaking">Speaking...</span>
					</div>
				{/if}
			</div>
		{:else}
			<div class="no-track">No voice narration available</div>
		{/if}
	</div>

	<div class="audio-actions">
		<button on:click={stopAll} class="btn btn-danger btn-block">
			⏹️ Stop All Audio
		</button>
	</div>
</div>

<style>
	.audio-player {
		height: 100%;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
		background: transparent;
		overflow-y: auto;
	}

	.audio-player h3 {
		margin: 0;
		font-size: 1.1rem;
		color: #ffd700;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
		text-align: center;
	}

	.audio-section {
		background: rgba(255, 255, 255, 0.08);
		border-radius: 0.6rem;
		padding: 0.6rem;
		border: 1px solid rgba(255, 255, 255, 0.15);
		backdrop-filter: blur(10px);
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.section-header h4 {
		margin: 0;
		font-size: 0.9rem;
		color: #a0aec0;
	}

	.volume-control {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.volume-control label {
		font-size: 0.9rem;
		color: #a0aec0;
		min-width: 60px;
	}

	.volume-slider {
		flex: 1;
		height: 6px;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 3px;
		outline: none;
		appearance: none;
	}

	.volume-slider::-webkit-slider-thumb {
		appearance: none;
		width: 18px;
		height: 18px;
		background: #ffd700;
		border-radius: 50%;
		cursor: pointer;
		box-shadow: 0 2px 4px rgba(0,0,0,0.3);
	}

	.volume-slider::-moz-range-thumb {
		width: 18px;
		height: 18px;
		background: #ffd700;
		border-radius: 50%;
		cursor: pointer;
		border: none;
		box-shadow: 0 2px 4px rgba(0,0,0,0.3);
	}

	.volume-display {
		font-size: 0.9rem;
		color: white;
		min-width: 40px;
		text-align: right;
	}

	.track-info {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 0.4rem;
		padding: 0.5rem;
	}

	.track-name {
		font-size: 0.8rem;
		color: white;
		margin-bottom: 0.3rem;
	}

	.no-track {
		color: rgba(255, 255, 255, 0.6);
		font-style: italic;
		text-align: center;
		padding: 1rem;
	}

	.equalizer {
		display: flex;
		gap: 3px;
		height: 20px;
		align-items: end;
	}

	.bar {
		width: 4px;
		background: #ffd700;
		border-radius: 2px;
		animation: bounce 1.2s ease-in-out infinite;
	}

	.bar:nth-child(1) { animation-delay: 0s; }
	.bar:nth-child(2) { animation-delay: 0.3s; }
	.bar:nth-child(3) { animation-delay: 0.6s; }
	.bar:nth-child(4) { animation-delay: 0.9s; }

	.voice-indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.speaking {
		color: #ffd700;
		font-weight: bold;
		animation: pulse 2s ease-in-out infinite;
	}

	.audio-actions {
		margin-top: auto;
	}

	.btn {
		border: none;
		border-radius: 0.5rem;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-small {
		padding: 0.4rem 0.8rem;
		font-size: 0.8rem;
	}

	.btn-block {
		width: 100%;
		padding: 0.8rem;
		font-size: 1rem;
	}

	.btn-playing {
		background: #48bb78;
		color: white;
	}

	.btn-playing:hover:not(:disabled) {
		background: #38a169;
	}

	.btn-danger {
		background: #e53e3e;
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background: #c53030;
		transform: translateY(-1px);
	}

	.btn:not(.btn-playing):not(.btn-danger) {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.btn:not(.btn-playing):not(.btn-danger):hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	@keyframes bounce {
		0%, 100% {
			height: 4px;
		}
		50% {
			height: 20px;
		}
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	@media (max-width: 1200px) {
		.audio-player {
			flex-direction: column;
			gap: 0.5rem;
		}

		.audio-section {
			padding: 0.5rem;
		}

		.section-header {
			margin-bottom: 0.3rem;
		}

		.volume-control {
			margin-bottom: 0.3rem;
		}
	}

	@media (max-width: 768px) {
		.audio-player {
			flex-direction: column;
		}

		.section-header {
			flex-direction: column;
			gap: 0.5rem;
			align-items: stretch;
		}

		.volume-control {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}

		.volume-control label {
			min-width: auto;
		}

		.volume-display {
			text-align: center;
		}
	}
</style>