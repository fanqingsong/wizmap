<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';

  // Live processing progress for a single dataset. Polls the backend until the
  // dataset reaches a terminal state (completed / failed), then exposes the
  // outcome via events and (for completed) a "View Visualization" action.
  export let datasetId: string;
  export let datasetName = '';

  const dispatch = createEventDispatcher();

  // API base URL configuration (mirrors DatasetUpload.svelte / MapView.svelte).
  const apiBase = window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : `https://${window.location.hostname}`;

  const POLL_MS = 2000;

  type DatasetInfo = {
    id: string;
    name: string;
    status: string;
    processing_progress: number;
    current_step: string | null;
    error_message: string | null;
    total_records: number | null;
  };

  let info: DatasetInfo | null = null;
  let loading = true;
  let connectionError = '';
  let pollTimer: ReturnType<typeof setInterval> | null = null;

  async function fetchStatus() {
    try {
      const response = await fetch(`${apiBase}/api/v1/datasets/${datasetId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = (await response.json()) as DatasetInfo;
      info = data;
      connectionError = '';
      if (data.name && !datasetName) {
        datasetName = data.name;
      }

      if (data.status === 'completed') {
        stopPolling();
        dispatch('completed', { datasetId: data.id });
      } else if (data.status === 'failed') {
        stopPolling();
        dispatch('failed', { datasetId: data.id, error: data.error_message });
      }
    } catch (error) {
      // Keep showing the last known state; just flag that we're retrying.
      connectionError = 'Lost connection to server — retrying…';
      console.error('Status poll failed:', error);
    } finally {
      loading = false;
    }
  }

  function startPolling() {
    stopPolling();
    pollTimer = setInterval(fetchStatus, POLL_MS);
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  function visualize() {
    if (datasetId) {
      window.location.href = `/?datasetId=${encodeURIComponent(datasetId)}`;
    }
  }

  $: percent = info ? Math.round((info.processing_progress || 0) * 100) : 0;
  $: status = info?.status ?? 'processing';
  $: isProcessing = status === 'processing' || status === 'uploading';
  $: isCompleted = status === 'completed';
  $: isFailed = status === 'failed';

  onMount(() => {
    fetchStatus().then(startPolling);
  });

  onDestroy(stopPolling);
</script>

<div class="processing-progress">
  <div class="progress-header">
    <div class="dataset-name" title={datasetName}>
      {datasetName || 'Dataset'}
    </div>
    <span class="status-badge {status}">
      {#if isProcessing}Processing{:else if isCompleted}Ready{:else if isFailed}Failed{:else}{status}{/if}
    </span>
  </div>

  {#if info?.total_records != null}
    <div class="records">{info.total_records.toLocaleString()} records</div>
  {/if}

  <!-- Progress bar -->
  <div class="progress-track" class:indeterminate={isProcessing && percent === 0}>
    <div
      class="progress-fill {status}"
      style="width: {isCompleted ? 100 : percent}%"
    ></div>
  </div>
  <div class="progress-meta">
    <span class="percent">{isCompleted ? 100 : percent}%</span>
    {#if isProcessing}
      <span class="step">{info?.current_step || 'Working…'}</span>
    {:else if isCompleted}
      <span class="step">Completed</span>
    {/if}
  </div>

  {#if isProcessing}
    <p class="hint">
      Generating embeddings can take several minutes for large datasets. The
      percentage updates between processing steps.
    </p>
  {/if}

  {#if connectionError}
    <p class="connection-error">{connectionError}</p>
  {/if}

  {#if isFailed}
    <div class="status-message error">
      <strong>Processing failed</strong>
      <p>{info?.error_message || 'An unexpected error occurred during processing.'}</p>
    </div>
  {/if}

  {#if isCompleted}
    <div class="status-message success">
      <strong>Ready to visualize!</strong>
      <p>Your dataset has been processed.</p>
      <button class="visualize-button" type="button" on:click={visualize}>
        View Visualization
      </button>
    </div>
  {/if}

  {#if loading && !info}
    <p class="hint">Connecting to processing pipeline…</p>
  {/if}
</div>

<style lang="scss">
  .processing-progress {
    font-family: 'Lato', sans-serif;
    color: #1f2937;
  }

  .progress-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 4px;
  }

  .dataset-name {
    font-size: 1rem;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .status-badge {
    flex-shrink: 0;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
    color: #fff;
    background: #6b7280;

    &.processing,
    &.uploading {
      background: #4f46e5;
    }

    &.completed {
      background: #10b981;
    }

    &.failed {
      background: #ef4444;
    }
  }

  .records {
    font-size: 0.8125rem;
    color: #6b7280;
    margin-bottom: 12px;
  }

  .progress-track {
    position: relative;
    height: 10px;
    background: #e5e7eb;
    border-radius: 999px;
    overflow: hidden;

    &.indeterminate::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      width: 40%;
      background: #4f46e5;
      border-radius: 999px;
      animation: indeterminate 1.4s ease-in-out infinite;
    }
  }

  .progress-fill {
    height: 100%;
    background: #4f46e5;
    border-radius: 999px;
    transition: width 0.4s ease;

    &.completed {
      background: #10b981;
    }

    &.failed {
      background: #ef4444;
    }
  }

  @keyframes indeterminate {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(350%);
    }
  }

  .progress-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 0.8125rem;

    .percent {
      font-weight: 600;
      color: #1f2937;
    }

    .step {
      color: #6b7280;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 60%;
    }
  }

  .hint {
    margin-top: 14px;
    font-size: 0.8125rem;
    color: #6b7280;
    line-height: 1.4;
  }

  .connection-error {
    margin-top: 10px;
    font-size: 0.8125rem;
    color: #b45309;
  }

  .status-message {
    margin-top: 16px;
    padding: 12px;
    border-radius: 8px;
    font-size: 0.875rem;

    strong {
      display: block;
      margin-bottom: 4px;
    }

    p {
      margin: 0;
      color: #6b7280;
    }

    &.success {
      background: #ecfdf5;
      border: 1px solid #a7f3d0;
    }

    &.error {
      background: #fef2f2;
      border: 1px solid #fecaca;

      strong {
        color: #b91c1c;
      }
    }
  }

  .visualize-button {
    margin-top: 10px;
    padding: 8px 14px;
    font-family: inherit;
    font-size: 0.875rem;
    font-weight: 600;
    color: #fff;
    background: #4f46e5;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s ease;

    &:hover {
      background: #4338ca;
    }
  }
</style>
