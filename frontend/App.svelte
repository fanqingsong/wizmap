<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import MapView from './src/components/mapview/MapView.svelte';
  import DatasetUpload from './src/components/dataset-upload/DatasetUpload.svelte';
  import ProcessingProgress from './src/components/dataset-upload/ProcessingProgress.svelte';

  // The map (display interface) is always shown. Uploads happen in a
  // right-side slide-out drawer toggled by the "+ Upload Dataset" button.
  let showUploadPanel = false;

  // Once a dataset is uploaded, the drawer switches from the upload form to a
  // live processing-progress view keyed to that dataset's id.
  let activeDatasetId = '';
  let activeDatasetName = '';

  $: drawerTitle = activeDatasetId ? 'Processing Dataset' : 'Upload Dataset';

  function openUploadPanel() {
    showUploadPanel = true;
  }

  function closeUploadPanel() {
    showUploadPanel = false;
  }

  function handleUploaded(event: CustomEvent) {
    activeDatasetId = event.detail.datasetId;
    activeDatasetName = event.detail.name || '';
  }

  // Drop the active dataset and go back to the upload form so the user can
  // upload another file.
  function uploadAnother() {
    activeDatasetId = '';
    activeDatasetName = '';
  }
</script>

<style lang="scss">
  .open-upload-button {
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 1000;
    padding: 8px 14px;
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    background: #4f46e5;
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    transition: background 0.15s ease;
  }

  .open-upload-button:hover {
    background: #4338ca;
  }

  .drawer-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1100;
    background: rgba(0, 0, 0, 0.3);
  }

  .upload-drawer {
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    width: 440px;
    max-width: 90vw;
    z-index: 1200;
    display: flex;
    flex-direction: column;
    background: #f9fafb;
    box-shadow: -4px 0 16px rgba(0, 0, 0, 0.15);
    overflow-y: auto;
  }

  .drawer-header {
    position: sticky;
    top: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;

    h2 {
      margin: 0;
      font-family: 'Lato', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: #1f2937;
    }
  }

  .drawer-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    font-size: 16px;
    line-height: 1;
    color: #6b7280;
    background: transparent;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  .drawer-close:hover {
    background: #f3f4f6;
    color: #1f2937;
  }

  .drawer-body {
    padding: 20px;
  }

  .upload-another {
    display: block;
    margin-top: 18px;
    padding: 0;
    font-family: 'Lato', sans-serif;
    font-size: 0.875rem;
    color: #4f46e5;
    background: transparent;
    border: none;
    cursor: pointer;
  }

  .upload-another:hover {
    text-decoration: underline;
  }

  /* Make the upload form fit the narrow drawer width. */
  .drawer-body :global(.dataset-upload-container) {
    max-width: none;
    margin: 0;
    box-shadow: none;
  }
</style>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Lato&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="stand-alone-page">
  <MapView />

  <button class="open-upload-button" type="button" on:click={openUploadPanel}>
    + Upload Dataset
  </button>

  {#if showUploadPanel}
    <div
      class="drawer-backdrop"
      on:click={closeUploadPanel}
      role="presentation"
      transition:fade={{ duration: 150 }}
    ></div>

    <aside class="upload-drawer" transition:fly={{ x: 440, duration: 250 }}>
      <div class="drawer-header">
        <h2>{drawerTitle}</h2>
        <button
          class="drawer-close"
          type="button"
          aria-label="Close"
          on:click={closeUploadPanel}
        >
          ✕
        </button>
      </div>
      <div class="drawer-body">
        {#if activeDatasetId}
          {#key activeDatasetId}
            <ProcessingProgress
              datasetId={activeDatasetId}
              datasetName={activeDatasetName}
            />
          {/key}
          <button class="upload-another" type="button" on:click={uploadAnother}>
            ← Upload another dataset
          </button>
        {:else}
          <DatasetUpload on:uploaded={handleUploaded} />
        {/if}
      </div>
    </aside>
  {/if}
</div>
