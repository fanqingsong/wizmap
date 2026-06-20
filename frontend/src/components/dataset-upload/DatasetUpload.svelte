<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let fileInput: HTMLInputElement;
  let isDragging = false;
  let selectedFile: File | null = null;
  let isUploading = false;
  let uploadProgress = 0;
  let uploadStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  let errorMessage = '';
  let datasetName = '';
  let datasetId = '';

  // API base URL configuration
  const apiBase = window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : `https://${window.location.hostname}`;

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      selectedFile = target.files[0];
      // Auto-generate dataset name from filename if not set
      if (!datasetName) {
        datasetName = selectedFile.name.replace(/\.[^/.]+$/, '');
      }
    }
  }

  function handleDragEnter(event: DragEvent) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave(event: DragEvent) {
    event.preventDefault();
    isDragging = false;
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    isDragging = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      selectedFile = event.dataTransfer.files[0];
      // Auto-generate dataset name from filename if not set
      if (!datasetName) {
        datasetName = selectedFile.name.replace(/\.[^/.]+$/, '');
      }
    }
  }

  async function uploadFile() {
    if (!selectedFile) {
      errorMessage = 'Please select a file first';
      uploadStatus = 'error';
      return;
    }

    if (!datasetName.trim()) {
      errorMessage = 'Please provide a dataset name';
      uploadStatus = 'error';
      return;
    }

    isUploading = true;
    uploadStatus = 'uploading';
    uploadProgress = 0;
    errorMessage = '';

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('name', datasetName);

    try {
      const response = await fetch(`${apiBase}/api/v1/datasets`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        datasetId = data.dataset_id;
        uploadStatus = 'success';
        uploadProgress = 100;

        // Dispatch event with dataset info
        dispatch('uploaded', {
          datasetId: data.dataset_id,
          name: datasetName,
          status: data.status
        });
      } else {
        const error = await response.json();
        errorMessage = error.detail || 'Upload failed';
        uploadStatus = 'error';
      }
    } catch (error) {
      errorMessage = 'Network error during upload';
      uploadStatus = 'error';
      console.error('Upload error:', error);
    } finally {
      isUploading = false;
    }
  }

  function resetUpload() {
    selectedFile = null;
    datasetName = '';
    datasetId = '';
    uploadStatus = 'idle';
    uploadProgress = 0;
    errorMessage = '';
    if (fileInput) {
      fileInput.value = '';
    }
  }

  function visualizeDataset() {
    if (datasetId) {
      // Redirect to visualization with dataset ID
      window.location.href = `/?datasetId=${datasetId}`;
    }
  }
</script>

<div class="dataset-upload-container">
  <div class="upload-header">
    <h2>Upload Dataset</h2>
    <p>Upload a text file to create an interactive visualization</p>
  </div>

  <div class="upload-content">
    <!-- File Drop Zone -->
    <div
      class="drop-zone {isDragging ? 'dragging' : ''} {selectedFile ? 'has-file' : ''}"
      on:dragenter={handleDragEnter}
      on:dragleave={handleDragLeave}
      on:dragover={handleDragOver}
      on:drop={handleDrop}
      on:click={() => fileInput.click()}
      role="button"
      tabindex="0"
    >
      <input
        type="file"
        bind:this={fileInput}
        on:change={handleFileSelect}
        accept=".txt,.csv,.json"
        hidden
      />

      {#if selectedFile}
        <div class="file-info">
          <svg class="file-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
          </svg>
          <div class="file-details">
            <div class="file-name">{selectedFile.name}</div>
            <div class="file-size">{(selectedFile.size / 1024).toFixed(1)} KB</div>
          </div>
          <button
            class="remove-file"
            on:click={(e) => {
              e.stopPropagation();
              selectedFile = null;
              if (fileInput) fileInput.value = '';
            }}
            type="button"
          >
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      {:else}
        <div class="drop-zone-content">
          <svg class="upload-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          <div class="drop-zone-text">
            <strong>Click to upload</strong> or drag and drop
          </div>
          <div class="drop-zone-hint">
            Supports .txt, .csv, .json files
          </div>
        </div>
      {/if}
    </div>

    <!-- Dataset Name Input -->
    <div class="form-group">
      <label for="dataset-name">Dataset Name</label>
      <input
        type="text"
        id="dataset-name"
        bind:value={datasetName}
        placeholder="Enter a name for your dataset"
        disabled={isUploading}
      />
    </div>

    <!-- Upload Button -->
    <button
      class="upload-button"
      on:click={uploadFile}
      disabled={!selectedFile || isUploading}
      type="button"
    >
      {#if isUploading}
        <span class="spinner"></span>
        Uploading...
      {:else}
        Upload & Process
      {/if}
    </button>

    <!-- Status Messages -->
    {#if uploadStatus === 'uploading'}
      <div class="status-message uploading">
        <div class="progress-bar">
          <div class="progress-fill" style="width: {uploadProgress}%"></div>
        </div>
        <p>Processing your dataset... This may take a few minutes.</p>
      </div>
    {/if}

    {#if uploadStatus === 'success'}
      <div class="status-message success">
        <svg class="status-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div>
          <strong>Upload successful!</strong>
          <p>Your dataset "{datasetName}" has been processed and is ready for visualization.</p>
          <button class="visualize-button" on:click={visualizeDataset} type="button">
            View Visualization
          </button>
          <button class="upload-another-button" on:click={resetUpload} type="button">
            Upload Another Dataset
          </button>
        </div>
      </div>
    {/if}

    {#if uploadStatus === 'error'}
      <div class="status-message error">
        <svg class="status-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div>
          <strong>Upload failed</strong>
          <p>{errorMessage}</p>
          <button class="retry-button" on:click={resetUpload} type="button">
            Try Again
          </button>
        </div>
      </div>
    {/if}
  </div>

  <!-- Help Section -->
  <div class="upload-help">
    <h3>Supported File Formats</h3>
    <ul>
      <li><strong>.txt</strong> - Plain text file (one document per line)</li>
      <li><strong>.csv</strong> - CSV file (first column contains text data)</li>
      <li><strong>.json</strong> - JSON array or object with text fields</li>
    </ul>
    <h3>What happens next?</h3>
    <ol>
      <li>Your file is uploaded to our secure storage</li>
      <li>We process the text using machine learning models</li>
      <li>The data is transformed into an interactive 2D visualization</li>
      <li>You can explore clusters, patterns, and topics in your data</li>
    </ol>
  </div>
</div>

<style lang="scss">
.dataset-upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;

  .upload-header {
    text-align: center;
    margin-bottom: 2rem;

    h2 {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #1f2937;
    }

    p {
      color: #6b7280;
      font-size: 1rem;
    }
  }

  .upload-content {
    background: white;
    border-radius: 0.5rem;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .drop-zone {
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #f9fafb;

    &:hover {
      border-color: #3b82f6;
      background: #eff6ff;
    }

    &.dragging {
      border-color: #3b82f6;
      background: #eff6ff;
      transform: scale(1.02);
    }

    &.has-file {
      border-color: #10b981;
      background: #f0fdf4;
    }
  }

  .drop-zone-content {
    .upload-icon {
      width: 3rem;
      height: 3rem;
      color: #9ca3af;
      margin: 0 auto 1rem;
    }

    .drop-zone-text {
      font-size: 1.125rem;
      color: #374151;
      margin-bottom: 0.5rem;
    }

    .drop-zone-hint {
      font-size: 0.875rem;
      color: #6b7280;
    }
  }

  .file-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;

    .file-icon {
      width: 2.5rem;
      height: 2.5rem;
      color: #3b82f6;
      flex-shrink: 0;
    }

    .file-details {
      flex: 1;
      text-align: left;

      .file-name {
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 0.25rem;
      }

      .file-size {
        font-size: 0.875rem;
        color: #6b7280;
      }
    }

    .remove-file {
      background: none;
      border: none;
      padding: 0.5rem;
      cursor: pointer;
      color: #6b7280;
      transition: color 0.2s;

      &:hover {
        color: #ef4444;
      }

      svg {
        width: 1.25rem;
        height: 1.25rem;
      }
    }
  }

  .form-group {
    margin-top: 1.5rem;

    label {
      display: block;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.5rem;
    }

    input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      font-size: 1rem;
      transition: border-color 0.2s;

      &:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }

      &:disabled {
        background-color: #f3f4f6;
        cursor: not-allowed;
      }
    }
  }

  .upload-button {
    width: 100%;
    margin-top: 1.5rem;
    padding: 0.875rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;

    &:hover:not(:disabled) {
      background: #2563eb;
    }

    &:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }

    .spinner {
      width: 1rem;
      height: 1rem;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .status-message {
    margin-top: 1.5rem;
    padding: 1rem;
    border-radius: 0.375rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;

    .status-icon {
      width: 1.5rem;
      height: 1.5rem;
      flex-shrink: 0;
      margin-top: 0.125rem;
    }

    p {
      margin: 0.5rem 0;
      color: #374151;
    }

    &.uploading {
      background: #eff6ff;
      border: 1px solid #bfdbfe;

      .progress-bar {
        width: 100%;
        height: 0.5rem;
        background: #dbeafe;
        border-radius: 0.25rem;
        overflow: hidden;
        margin-bottom: 0.5rem;

        .progress-fill {
          height: 100%;
          background: #3b82f6;
          transition: width 0.3s ease;
          animation: pulse 2s infinite;
        }
      }
    }

    &.success {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;

      .status-icon {
        color: #10b981;
      }

      strong {
        color: #065f46;
      }
    }

    &.error {
      background: #fef2f2;
      border: 1px solid #fecaca;

      .status-icon {
        color: #ef4444;
      }

      strong {
        color: #991b1b;
      }
    }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .visualize-button,
  .upload-another-button,
  .retry-button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    margin-right: 0.5rem;
    transition: background 0.2s;
  }

  .visualize-button {
    background: #10b981;
    color: white;

    &:hover {
      background: #059669;
    }
  }

  .upload-another-button,
  .retry-button {
    background: #6b7280;
    color: white;

    &:hover {
      background: #4b5563;
    }
  }

  .upload-help {
    background: #f9fafb;
    border-radius: 0.5rem;
    padding: 1.5rem;

    h3 {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: #1f2937;
    }

    ul, ol {
      margin: 0;
      padding-left: 1.5rem;
      color: #4b5563;

      li {
        margin-bottom: 0.5rem;
        line-height: 1.5;

        strong {
          color: #1f2937;
        }
      }
    }

    ul {
      margin-bottom: 1.5rem;
    }
  }
}
</style>
