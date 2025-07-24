<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import { createEventDispatcher } from 'svelte';

	export let messages: Array<{
		player_name: string;
		message: string;
		timestamp: number;
	}> = [];
	export let playerName: string = '';
	export let gameId: string = '';

	const dispatch = createEventDispatcher();

	let chatContainer: HTMLElement;
	let messageInput = '';

	afterUpdate(() => {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	});

	function sendMessage() {
		if (!messageInput.trim()) return;

		dispatch('chat', {
			message: messageInput.trim(),
			game_id: gameId,
			player_name: playerName
		});

		messageInput = '';
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function formatTime(timestamp: number): string {
		const date = new Date(timestamp);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	function isOwnMessage(messageSender: string): boolean {
		return messageSender === playerName;
	}

	function isSystemMessage(messageSender: string): boolean {
		return messageSender === 'System';
	}
</script>

<div class="chat-window">
	<div class="chat-header">
		<h4>💬 Party Chat</h4>
		<div class="chat-status">
			{messages.length} messages
		</div>
	</div>

	<div class="chat-messages" bind:this={chatContainer}>
		{#if messages.length === 0}
			<div class="no-messages">
				<div class="no-messages-text">No messages yet...</div>
				<div class="no-messages-hint">Chat with your party members!</div>
			</div>
		{:else}
			{#each messages as message (message.timestamp)}
				<div 
					class="message" 
					class:own-message={isOwnMessage(message.player_name)}
					class:system-message={isSystemMessage(message.player_name)}
				>
					<div class="message-header">
						<span class="sender">{message.player_name}</span>
						<span class="timestamp">{formatTime(message.timestamp)}</span>
					</div>
					<div class="message-content">
						{message.message}
					</div>
				</div>
			{/each}
		{/if}
	</div>

	<div class="chat-input">
		<div class="input-container">
			<input
				type="text"
				bind:value={messageInput}
				on:keydown={handleKeydown}
				placeholder="Type a message to your party..."
				maxlength="200"
				class="message-input"
			/>
			<button 
				on:click={sendMessage}
				disabled={!messageInput.trim()}
				class="send-button"
			>
				📤
			</button>
		</div>
		<div class="chat-hint">
			Press Enter to send • Shift+Enter for new line
		</div>
	</div>
</div>

<style>
	.chat-window {
		height: 100%;
		display: flex;
		flex-direction: column;
		background: rgba(255, 255, 255, 0.05);
		border-radius: 1rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
	}

	.chat-header {
		background: rgba(255, 255, 255, 0.1);
		padding: 0.8rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-shrink: 0;
	}

	.chat-header h4 {
		margin: 0;
		font-size: 1.1rem;
		color: #ffd700;
	}

	.chat-status {
		font-size: 0.8rem;
		color: #a0aec0;
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		padding: 0.8rem;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
		min-height: 0;
		height: 100%;
	}

	.chat-messages::-webkit-scrollbar {
		width: 6px;
	}

	.chat-messages::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 3px;
	}

	.chat-messages::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
	}

	.no-messages {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: rgba(255, 255, 255, 0.6);
		text-align: center;
	}

	.no-messages-text {
		font-size: 1.1rem;
		margin-bottom: 0.5rem;
	}

	.no-messages-hint {
		font-size: 0.9rem;
		font-style: italic;
	}

	.message {
		background: rgba(255, 255, 255, 0.1);
		border-radius: 0.8rem;
		padding: 0.8rem;
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all 0.2s ease;
	}

	.message:hover {
		background: rgba(255, 255, 255, 0.15);
	}

	.message.own-message {
		background: rgba(102, 126, 234, 0.2);
		border-color: rgba(102, 126, 234, 0.4);
		margin-left: 2rem;
	}

	.message-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.sender {
		font-weight: bold;
		color: #ffd700;
		font-size: 0.9rem;
	}

	.own-message .sender {
		color: #9bb5ff;
	}

	.message.system-message {
		background: rgba(255, 215, 0, 0.15);
		border-color: rgba(255, 215, 0, 0.4);
		margin: 0;
		text-align: center;
	}

	.system-message .sender {
		color: #ffd700;
		font-weight: bold;
	}

	.system-message .message-content {
		font-style: italic;
		color: rgba(255, 255, 255, 0.9);
	}

	.timestamp {
		font-size: 0.8rem;
		color: #a0aec0;
	}

	.message-content {
		color: white;
		line-height: 1.4;
		word-wrap: break-word;
	}

	.chat-input {
		background: rgba(255, 255, 255, 0.15);
		padding: 0.8rem;
		border-top: 2px solid rgba(255, 215, 0, 0.3);
		backdrop-filter: blur(15px);
		flex-shrink: 0;
	}

	.input-container {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 0.3rem;
	}

	.message-input {
		flex: 1;
		padding: 0.6rem;
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.4rem;
		color: white;
		font-size: 0.85rem;
		font-family: inherit;
		transition: all 0.3s ease;
	}

	.message-input:focus {
		outline: none;
		border-color: #ffd700;
		box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
	}

	.message-input::placeholder {
		color: rgba(255, 255, 255, 0.5);
	}

	.send-button {
		padding: 0.6rem 0.8rem;
		background: #ffd700;
		color: #1a1a2e;
		border: none;
		border-radius: 0.4rem;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.3s ease;
		font-weight: bold;
		min-width: 45px;
	}

	.send-button:hover:not(:disabled) {
		background: #ffed4e;
		transform: translateY(-1px);
	}

	.send-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.chat-hint {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.6);
		text-align: center;
		font-style: italic;
	}

	@media (max-width: 1200px) {
		.chat-messages {
			padding: 0.6rem;
		}

		.chat-header {
			padding: 0.6rem;
		}

		.chat-input {
			padding: 0.6rem;
		}
	}

	@media (max-width: 768px) {
		.chat-header {
			padding: 0.8rem;
		}

		.chat-messages {
			padding: 0.8rem;
			min-height: 150px;
			max-height: 250px;
		}

		.chat-input {
			padding: 0.8rem;
		}

		.message {
			padding: 0.6rem;
		}

		.message.own-message {
			margin-left: 1rem;
		}

		.input-container {
			flex-direction: column;
			gap: 0.5rem;
		}

		.send-button {
			width: 100%;
		}
	}
</style>