<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let isMyTurn: boolean = false;
	export let currentPlayer: string = '';
	export let gameStatus: string = 'waiting';
	export let actionsNeeded: number = 0;
	export let actionsReceived: number = 0;
	export let waitingFor: string[] = [];
	export let hasSubmittedAction: boolean = false;

	const dispatch = createEventDispatcher();

	let actionText = '';
	let selectedActionType = 'action';


	function submitAction() {
		if (!actionText.trim()) {
			alert('Please enter an action!');
			return;
		}

		dispatch('action', {
			type: 'action',
			text: actionText.trim()
		});

		actionText = '';
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			if (isMyTurn) {
				submitAction();
			}
		}
	}

	function getPlaceholderText(): string {
		return 'Describe what your character wants to do...';
	}
</script>

<div class="action-section">
	<div class="action-header">
		<h3>🎭 Round Actions</h3>
		<div class="action-status">
			{#if hasSubmittedAction}
				<div class="submitted-indicator">
					<span class="submitted-text">✅ Action submitted!</span>
					{#if actionsReceived < actionsNeeded}
						<div class="waiting-others">
							<span>Waiting for: {waitingFor.join(', ')}</span>
							<div class="spinner"></div>
						</div>
					{/if}
				</div>
			{:else if isMyTurn}
				<div class="turn-indicator">
					<span class="turn-text">Your turn to act!</span>
				</div>
			{/if}
			<div class="action-counter">
				{actionsReceived}/{actionsNeeded} actions received
			</div>
		</div>
	</div>

	<div class="action-container" class:disabled={!isMyTurn || hasSubmittedAction}>
		<div class="action-input">
			<label for="action-text" class="input-label">
				What does your character do?
			</label>
			<textarea 
				id="action-text"
				bind:value={actionText}
				on:keydown={handleKeydown}
				placeholder={getPlaceholderText()}
				disabled={!isMyTurn || hasSubmittedAction}
				rows="4"
				class="action-textarea"
			></textarea>
			<div class="input-hint">
				Be descriptive - explain what your character says, does, or attempts to accomplish.
			</div>
		</div>
	</div>
</div>

<style>
	.action-section {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 1rem;
		padding: 1.5rem;
		border: 2px solid rgba(255, 255, 255, 0.1);
	}

	.action-header {
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid rgba(255, 255, 255, 0.1);
	}

	.action-header h3 {
		margin: 0 0 1rem 0;
		font-size: 1.4rem;
		color: #ffd700;
		text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
	}

	.action-status {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.submitted-indicator {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.submitted-text {
		color: #48bb78;
		font-weight: bold;
	}

	.waiting-others {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #a0aec0;
		font-size: 0.9rem;
	}

	.turn-indicator {
		color: #ffd700;
		font-weight: bold;
	}

	.action-counter {
		background: rgba(255, 255, 255, 0.1);
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.9rem;
		color: #a0aec0;
	}

	.spinner {
		width: 20px;
		height: 20px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top: 2px solid #ffd700;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.action-container {
		transition: all 0.3s ease;
	}

	.action-container.disabled {
		opacity: 0.6;
		pointer-events: none;
	}

	.input-hint {
		margin-top: 0.5rem;
		font-size: 0.85rem;
		color: #a0aec0;
		font-style: italic;
	}

	.action-input {
		margin-bottom: 1.5rem;
	}

	.input-label {
		display: block;
		font-weight: bold;
		margin-bottom: 0.8rem;
		color: white;
	}

	.action-textarea {
		width: 100%;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.1);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.8rem;
		color: white;
		font-size: 1rem;
		line-height: 1.5;
		resize: vertical;
		font-family: inherit;
		transition: all 0.3s ease;
	}

	.action-textarea:focus {
		outline: none;
		border-color: #ffd700;
		box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
	}

	.action-textarea::placeholder {
		color: rgba(255, 255, 255, 0.5);
		font-style: italic;
	}

	.action-textarea:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}


	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	@media (max-width: 768px) {
		.action-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
			text-align: center;
		}
	}
</style>