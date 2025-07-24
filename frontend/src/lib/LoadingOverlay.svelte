<script lang="ts">
	export let isVisible: boolean = false;
	export let message: string = 'Loading...';
</script>

{#if isVisible}
	<div class="loading-overlay">
		<div class="loading-content">
			<div class="loading-spinner">
				<div class="spinner-ring"></div>
				<div class="spinner-icon">🎲</div>
			</div>
			<h3>Game Master at Work</h3>
			<p>{message}</p>
			<div class="loading-tips">
				<div class="tip">✨ Creating your story experience</div>
				<div class="tip">🎭 This may take a few moments</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		background: rgba(26, 26, 46, 0.95);
		backdrop-filter: blur(10px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.3s ease-out;
	}

	.loading-content {
		text-align: center;
		color: white;
		max-width: 400px;
		padding: 3rem 2rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 1.5rem;
		border: 2px solid rgba(255, 215, 0, 0.3);
		backdrop-filter: blur(20px);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
	}

	.loading-spinner {
		position: relative;
		width: 80px;
		height: 80px;
		margin: 0 auto 2rem;
	}

	.spinner-ring {
		position: absolute;
		width: 80px;
		height: 80px;
		border: 4px solid rgba(255, 215, 0, 0.2);
		border-top: 4px solid #ffd700;
		border-radius: 50%;
		animation: spin 1.5s linear infinite;
	}

	.spinner-icon {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		font-size: 2rem;
		animation: bounce 2s ease-in-out infinite;
	}

	.loading-content h3 {
		font-size: 1.8rem;
		margin-bottom: 1rem;
		color: #ffd700;
		text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
	}

	.loading-content p {
		font-size: 1.1rem;
		margin-bottom: 2rem;
		color: rgba(255, 255, 255, 0.9);
		line-height: 1.4;
	}

	.loading-tips {
		display: flex;
		flex-direction: column;
		gap: 0.8rem;
	}

	.tip {
		background: rgba(255, 255, 255, 0.1);
		padding: 0.8rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.9rem;
		color: rgba(255, 255, 255, 0.8);
		border-left: 3px solid #ffd700;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	@keyframes bounce {
		0%, 100% {
			transform: translate(-50%, -50%) scale(1);
		}
		50% {
			transform: translate(-50%, -50%) scale(1.1);
		}
	}

	@media (max-width: 768px) {
		.loading-content {
			margin: 1rem;
			padding: 2rem 1.5rem;
		}

		.loading-content h3 {
			font-size: 1.5rem;
		}

		.loading-content p {
			font-size: 1rem;
		}

		.loading-spinner {
			width: 60px;
			height: 60px;
		}

		.spinner-ring {
			width: 60px;
			height: 60px;
		}

		.spinner-icon {
			font-size: 1.5rem;
		}
	}
</style>