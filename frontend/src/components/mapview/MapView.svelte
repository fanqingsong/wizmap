<script lang="ts">
  import { onMount } from 'svelte';
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

  // Backend API base (mirrors DatasetUpload.svelte).
  const apiBase = window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : `https://${window.location.hostname}`;

  // Uploaded datasets that are ready to visualize. Fetched on mount so the
  // selector on the map can list them alongside the built-in presets.
  type UploadedDataset = {
    id: string;
    name: string;
    status: string;
    total_records: number | null;
  };
  let uploadedDatasets: UploadedDataset[] = [];

  // If the current view is backed by an uploaded dataset, remember its id so
  // the selector can highlight the active option.
  let currentDatasetId = '';

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
      currentDatasetId = datasetId;
      // Use backend API to load dataset data
      dataURL = `${apiBase}/api/v1/datasets/${datasetId}/data`;
      gridURL = `${apiBase}/api/v1/datasets/${datasetId}/grid`;
      console.log('Loading from backend API:', { dataURL, gridURL });
    }
  }

  onMount(async () => {
    try {
      const response = await fetch(`${apiBase}/api/v1/datasets`);
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as UploadedDataset[];
      uploadedDatasets = data.filter((d) => d.status === 'completed');
    } catch (error) {
      console.error('Failed to load uploaded datasets:', error);
    }
  });

  // Value currently selected in the dropdown: the active uploaded dataset id
  // when viewing one, otherwise the active preset datasetName.
  $: selectedDatasetValue = currentDatasetId || datasetName;

  // Handle a selection from the combined (built-in + uploaded) dropdown.
  // Built-in datasets switch in place without a reload; uploaded datasets
  // require a reload so the backend-resolved data/grid URLs are fetched fresh.
  function selectDataset(event: Event) {
    const target = event.target as HTMLSelectElement;
    const value = target.value;

    if (presetDatasets.some((ds) => ds.value === value)) {
      datasetName = value;
      dataURL = null;
      gridURL = null;
      currentDatasetId = '';

      // Reflect the choice in the URL (replace, no reload / no history entry).
      const url = new URL(window.location.href);
      url.searchParams.set('dataset', datasetName);
      url.searchParams.delete('datasetId');
      url.searchParams.delete('dataURL');
      url.searchParams.delete('gridURL');
      window.history.replaceState({}, '', url.toString());
    } else if (value) {
      window.location.href = `/?datasetId=${encodeURIComponent(value)}`;
    }
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
  <div class="dataset-selector">
    <label for="preset-dataset-select">Dataset</label>
    <select
      id="preset-dataset-select"
      value={selectedDatasetValue}
      on:change={selectDataset}
    >
      <optgroup label="Built-in">
        {#each presetDatasets as ds}
          <option value={ds.value}>{ds.label}</option>
        {/each}
      </optgroup>
      <optgroup label="Uploaded">
        {#if uploadedDatasets.length === 0}
          <option value="" disabled>No uploaded datasets yet</option>
        {:else}
          {#each uploadedDatasets as ds}
            <option value={ds.id}>
              {ds.name}{ds.total_records ? ` (${ds.total_records} rows)` : ''}
            </option>
          {/each}
        {/if}
      </optgroup>
    </select>
  </div>

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
