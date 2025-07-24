<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';

	export let story: string = '';
	export let storyHistory: Array<{
		text: string;
		voice_file?: string;
		background_music?: string;
	}> = [];

	let storyContainer: HTMLElement;
	let showHistory = false;

	afterUpdate(() => {
		if (storyContainer) {
			storyContainer.scrollTop = storyContainer.scrollHeight;
		}
	});

	function toggleHistory() {
		showHistory = !showHistory;
	}
</script>

<div class="story-section">
	<div class="story-header">
		<h3>📖 The Tale Unfolds</h3>
		<button 
			on:click={toggleHistory} 
			class="btn btn-secondary"
			disabled={storyHistory.length === 0}
		>
			{showHistory ? 'Hide' : 'Show'} History ({storyHistory.length})
		</button>
	</div>

	<div class="story-container" bind:this={storyContainer}>
		{#if showHistory && storyHistory.length > 0}
			<div class="story-history">
				<h4>📜 Previous Events</h4>
				{#each storyHistory.slice(0, -1) as segment, index}
					<div class="story-segment historical">
						<div class="segment-number">Chapter {index + 1}</div>
						<div class="segment-text">{segment.text}</div>
						{#if segment.voice_file}
							<div class="segment-meta">
								🎵 Voice narration available
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}

		{#if story}
			<div class="current-story">
				<h4>🌟 Current Scene</h4>
				<div class="story-text">
					{story}
				</div>
			</div>
		{:else if storyHistory.length === 0}
			<div class="waiting-state">
				<div class="waiting-animation">
					<div class="waiting-icon">🗡️</div>
					<h3>Preparing Your Adventure</h3>
					<p>The Game Master is setting the scene...</p>
					<div class="progress-dots">
						<div class="dot"></div>
						<div class="dot"></div>
						<div class="dot"></div>
						<div class="dot"></div>
					</div>
					<div class="waiting-tips">
						<div class="tip">💡 <strong>Tip:</strong> Use the chat to coordinate with your party</div>
						<div class="tip">⚔️ <strong>Ready?</strong> Your adventure will begin shortly</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.story-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
		overflow: hidden;
	}

	.story-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid rgba(255, 255, 255, 0.1);
	}

	.story-header h3 {
		margin: 0;
		font-size: 1.4rem;
		color: #ffd700;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
	}

	.story-container {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		background: rgba(0, 0, 0, 0.2);
		border-radius: 0.8rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.story-container::-webkit-scrollbar {
		width: 8px;
	}

	.story-container::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 4px;
	}

	.story-container::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.3);
		border-radius: 4px;
	}

	.story-container::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.5);
	}

	.story-history h4, .current-story h4 {
		margin: 0 0 1rem 0;
		font-size: 1.2rem;
		color: #a0aec0;
	}

	.story-segment {
		margin-bottom: 1.5rem;
		padding: 1rem;
		border-radius: 0.5rem;
	}

	.story-segment.historical {
		background: rgba(255, 255, 255, 0.05);
		border-left: 3px solid #4a5568;
	}

	.segment-number {
		font-size: 0.9rem;
		color: #ffd700;
		font-weight: bold;
		margin-bottom: 0.5rem;
	}

	.segment-text {
		line-height: 1.6;
		color: rgba(255, 255, 255, 0.9);
		font-size: 1rem;
	}

	.segment-meta {
		margin-top: 0.5rem;
		font-size: 0.8rem;
		color: #a0aec0;
		font-style: italic;
	}

	.current-story {
		background: rgba(255, 215, 0, 0.1);
		border: 2px solid rgba(255, 215, 0, 0.3);
		border-radius: 0.8rem;
		padding: 1.5rem;
		margin-top: 1rem;
	}

	.story-text {
		font-size: 1.1rem;
		line-height: 1.7;
		color: white;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
	}

	.waiting-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		min-height: 300px;
		background: radial-gradient(circle at center, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
		border-radius: 1rem;
	}

	.waiting-animation {
		text-align: center;
		color: white;
		max-width: 400px;
		padding: 2rem;
	}

	.waiting-icon {
		font-size: 4rem;
		margin-bottom: 1.5rem;
		animation: float 3s ease-in-out infinite;
		filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.5));
	}

	.waiting-animation h3 {
		font-size: 1.8rem;
		margin-bottom: 1rem;
		color: #ffd700;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
	}

	.waiting-animation p {
		font-size: 1.2rem;
		margin-bottom: 2rem;
		color: rgba(255, 255, 255, 0.9);
	}

	.progress-dots {
		display: flex;
		justify-content: center;
		gap: 0.8rem;
		margin-bottom: 2rem;
	}

	.dot {
		width: 12px;
		height: 12px;
		background: #ffd700;
		border-radius: 50%;
		animation: bounce 1.4s ease-in-out infinite both;
	}

	.dot:nth-child(1) { animation-delay: -0.32s; }
	.dot:nth-child(2) { animation-delay: -0.16s; }
	.dot:nth-child(3) { animation-delay: 0s; }
	.dot:nth-child(4) { animation-delay: 0.16s; }

	.waiting-tips {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.tip {
		background: rgba(255, 255, 255, 0.1);
		padding: 1rem;
		border-radius: 0.8rem;
		border-left: 4px solid #ffd700;
		text-align: left;
		font-size: 0.95rem;
		line-height: 1.4;
		backdrop-filter: blur(10px);
	}

	.tip strong {
		color: #ffd700;
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

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: rgba(255, 255, 255, 0.1);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.btn-secondary:hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0px);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 0.4;
		}
		50% {
			opacity: 1;
		}
	}

	@media (max-width: 768px) {
		.story-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}
		
		.story-section {
			max-height: 50vh;
		}
		
		.story-container {
			padding: 0.8rem;
		}
		
		.current-story {
			padding: 1rem;
		}
		
		.story-text {
			font-size: 1rem;
			line-height: 1.6;
		}
	}

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0.8);
			opacity: 0.5;
		}
		40% {
			transform: scale(1.2);
			opacity: 1;
		}
	}
</style>