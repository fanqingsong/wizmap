<script lang="ts">
  // import DiffusiondbVis from './src/components/diffusiondbvis/DiffusiondbVis.svelte';
  import MapView from './src/components/mapview/MapView.svelte';
  import DatasetUpload from './src/components/dataset-upload/DatasetUpload.svelte';

  // Show the upload view whenever there is no dataset selected. A dataset is
  // considered selected once the URL carries a `datasetId` (set by the upload
  // flow after a successful upload) or a legacy `dataset`/`dataURL` param.
  let showUpload = (() => {
    const params = new URLSearchParams(window.location.search);
    return (
      window.location.search === '' ||
      (!params.has('datasetId') &&
        !params.has('dataset') &&
        !params.has('dataURL'))
    );
  })();

  function openUpload() {
    showUpload = true;
  }

  function closeUpload() {
    showUpload = false;
  }
</script>

<style>
  .upload-view {
    position: relative;
  }

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

  .back-to-map-button {
    display: block;
    margin: 0 auto 24px;
    padding: 8px 14px;
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    color: #4f46e5;
    background: transparent;
    border: none;
    cursor: pointer;
  }

  .back-to-map-button:hover {
    text-decoration: underline;
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
  {#if showUpload}
    <div class="upload-view">
      <DatasetUpload />
      <button class="back-to-map-button" type="button" on:click={closeUpload}>
        ← Explore demo data
      </button>
    </div>
  {:else}
    <!-- <DiffusiondbVis /> -->
    <MapView />
    <button class="open-upload-button" type="button" on:click={openUpload}>
      + Upload Dataset
    </button>
  {/if}
</div>
