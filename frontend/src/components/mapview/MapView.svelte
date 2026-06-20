<script lang="ts">
  import {
    getFloatingWindowStore,
    getFooterStore,
    getSearchBarStore
  } from '../../stores';
  import Embedding from '../embedding/Embedding.svelte';
  import Footer from '../footer/Footer.svelte';
  import SearchPanel from '../search-panel/SearchPanel.svelte';

  let component: HTMLElement | null = null;
  let datasetName = 'acl-abstracts';
  // let datasetName = 'temp';
  let dataURL: string | null = null;
  let gridURL: string | null = null;
  let notebookMode = false;

  // Preset datasets available for selection in the UI.
  // `value` must match the keys handled in Embedding.svelte's switch().
  const presetDatasets = [
    { value: 'acl-abstracts', label: 'ACL Paper Abstracts (63k)' },
    { value: 'diffusiondb', label: 'DiffusionDB Prompts + Images (1.8M)' },
    { value: 'imdb', label: 'IMDB Reviews (25k)' }
  ];

  // Check url query to change dataset names
  if (window.location.search !== '') {
    const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('dataset')) {
      datasetName = searchParams.get('dataset')!;
    }

    if (searchParams.has('dataURL') && searchParams.has('gridURL')) {
      dataURL = searchParams.get('dataURL') as string;
      gridURL = searchParams.get('gridURL') as string;
      console.log(dataURL, gridURL);
    }

    // Support for backend API dataset loading
    if (searchParams.has('datasetId')) {
      const datasetId = searchParams.get('datasetId')!;
      // Use backend API to load dataset data
      const apiBase = window.location.hostname === 'localhost'
        ? 'http://localhost:8080'
        : `https://${window.location.hostname}`;
      dataURL = `${apiBase}/api/v1/datasets/${datasetId}/data`;
      gridURL = `${apiBase}/api/v1/datasets/${datasetId}/grid`;
      console.log('Loading from backend API:', { dataURL, gridURL });
    }
  }

  // Whether the current view is backed by a preset dataset (true) or a
  // custom datasetId/dataURL (false). When false we hide the preset selector
  // because switching would discard the custom data.
  const isPresetDataset = !dataURL && !gridURL;

  // Switch to a preset dataset without a full page reload.
  // Clears any custom dataURL/gridURL so Embedding falls back to the
  // datasetName-based loading, updates the URL for shareability, and lets the
  // {#key} block re-mount the Embedding component.
  function selectPreset(event: Event) {
    const target = event.target as HTMLSelectElement;
    datasetName = target.value;
    dataURL = null;
    gridURL = null;

    // Reflect the choice in the URL (replace, no reload / no history entry).
    const url = new URL(window.location.href);
    url.searchParams.set('dataset', datasetName);
    url.searchParams.delete('datasetId');
    url.searchParams.delete('dataURL');
    url.searchParams.delete('gridURL');
    window.history.replaceState({}, '', url.toString());
  }

  if (import.meta.env.MODE === 'notebook') {
    notebookMode = true;
  }

  // Create stores for child components to consume
  const footerStore = getFooterStore();
  const searchBarStore = getSearchBarStore();
  const floatingWindowStore = getFloatingWindowStore();
</script>

<style lang="scss">
  @use './MapView.scss' as *;
</style>

<div class="mapview-page">
  {#if isPresetDataset}
    <div class="dataset-selector">
      <label for="preset-dataset-select">Dataset</label>
      <select
        id="preset-dataset-select"
        value={datasetName}
        on:change={selectPreset}
      >
        {#each presetDatasets as ds}
          <option value={ds.value}>{ds.label}</option>
        {/each}
      </select>
    </div>
  {/if}

  <div id="popper-tooltip-top" class="popper-tooltip hidden" role="tooltip">
    <span class="popper-content"></span>
    <div class="popper-arrow"></div>
  </div>

  <div id="popper-tooltip-bottom" class="popper-tooltip hidden" role="tooltip">
    <span class="popper-content"></span>
    <div class="popper-arrow"></div>
  </div>

  <div class="app-wrapper">
    <div class="main-app" bind:this="{component}">
      <div class="main-app-container">
        {#key datasetName}
          <Embedding
            {datasetName}
            {dataURL}
            {gridURL}
            {footerStore}
            {searchBarStore}
            {floatingWindowStore}
            {notebookMode}
          />
        {/key}
      </div>
    </div>
  </div>

  <div class="footer-container">
    <Footer {footerStore} />
  </div>

  <div class="search-panel-container">
    <SearchPanel searchPanelStore="{searchBarStore}" />
  </div>
</div>
