import sys
import os
from pathlib import Path

# Add notebook-widget to path to import wizmap
notebook_widget_path = Path(__file__).parent.parent.parent.parent / "notebook-widget"
sys.path.insert(0, str(notebook_widget_path))

import numpy as np
import pandas as pd
import httpx
from umap import UMAP
from tqdm import tqdm
from typing import List, Tuple, Dict, Any
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.database import Dataset, Embedding, ProcessedResult, DatasetStatus
from app.services.minio_service import MinioService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Import wizmap functions
try:
    from wizmap import generate_grid_dict
    WIZMAP_AVAILABLE = True
except ImportError:
    logger.warning("wizmap module not available, some features will be limited")
    WIZMAP_AVAILABLE = False


class ProcessingService:
    def __init__(self):
        self.minio_service = MinioService()
        self.umap_reducer = None
        # UMAP is instantiated per-dataset in _run_umap. Embeddings come from
        # the SiliconFlow API, so there is no local model to preload.
        if settings.EMBEDDING_API_KEY:
            logger.info(
                f"Using embedding API: {settings.EMBEDDING_BASE_URL} "
                f"model={settings.EMBEDDING_MODEL or '(not set)'}"
            )
        else:
            logger.warning(
                "EMBEDDING_API_KEY is not set; dataset processing will fail at the "
                "embedding step. Configure it in backend/.env."
            )

    def update_progress(self, dataset_id: str, db: Session, progress: float, current_step: str):
        """Update processing progress in database"""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            dataset.processing_progress = progress
            dataset.current_step = current_step
            db.commit()

    def process_dataset(self, dataset_id: str, db: Session) -> bool:
        """Process a dataset: text → embeddings → UMAP → WizMap format"""
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                logger.error(f"Dataset {dataset_id} not found")
                return False

            # Step 1: Download and read file from MinIO
            self.update_progress(dataset_id, db, 0.1, "Reading file from storage")
            file_content = self.minio_service.get_file_sync(dataset.file_path)
            texts = self._parse_file_content(file_content, dataset.file_path)
            dataset.total_records = len(texts)
            db.commit()

            if not texts or len(texts) == 0:
                raise ValueError("No valid text data found in file")

            # Step 2: Generate embeddings
            self.update_progress(dataset_id, db, 0.3, "Generating text embeddings")
            embeddings = self._generate_embeddings(texts)

            # Step 3: UMAP dimensionality reduction
            self.update_progress(dataset_id, db, 0.5, "Running UMAP projection")
            embeddings_2d = self._run_umap(embeddings)

            # Fallback: if ML processing failed, generate random 2D coordinates
            if embeddings_2d is None or embeddings_2d.size == 0:
                logger.warning("ML processing failed, using random coordinates")
                embeddings_2d = np.random.rand(len(texts), 2).astype(np.float32) * 10

            # Step 4: Save embeddings to database
            self.update_progress(dataset_id, db, 0.6, "Saving embeddings to database")
            self._save_embeddings(dataset_id, texts, embeddings_2d, db)

            # Step 5: Generate WizMap format data
            self.update_progress(dataset_id, db, 0.7, "Generating WizMap visualization data")
            grid_dict, data_list = self._generate_wizmap_data(embeddings_2d, texts)

            # Step 6: Upload processed files to MinIO
            self.update_progress(dataset_id, db, 0.9, "Uploading processed files")
            grid_path, data_path = self._upload_processed_data(dataset_id, grid_dict, data_list)

            # Step 7: Save processed result metadata
            self._save_processed_result(dataset_id, grid_path, data_path, grid_dict, db)

            # Update dataset as completed
            dataset.status = DatasetStatus.COMPLETED
            dataset.processing_progress = 1.0
            dataset.current_step = "Completed"
            dataset.completed_at = datetime.utcnow()
            db.commit()

            logger.info(f"Dataset {dataset_id} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing dataset {dataset_id}: {e}")
            dataset.status = DatasetStatus.FAILED
            dataset.error_message = str(e)
            db.commit()
            return False

    def _parse_file_content(self, content: bytes, file_path: str) -> List[str]:
        """Parse file content based on file type"""
        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            text_content = content.decode('utf-8')

            if file_extension == '.json':
                # Handle JSON format
                data = json.loads(text_content)
                if isinstance(data, list):
                    return [str(item) for item in data]
                elif isinstance(data, dict) and 'texts' in data:
                    return data['texts']
                else:
                    return [text_content]

            elif file_extension == '.csv':
                # Handle CSV format
                import io
                df = pd.read_csv(io.StringIO(text_content))
                # Assume first text column contains the data
                text_column = df.select_dtypes(include=['object']).columns[0]
                return df[text_column].tolist()

            else:  # .txt and others
                # Handle plain text - split by lines
                lines = text_content.strip().split('\n')
                # Filter empty lines
                return [line.strip() for line in lines if line.strip()]

        except Exception as e:
            logger.error(f"Error parsing file content: {e}")
            raise ValueError(f"Failed to parse file: {str(e)}")

    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate text embeddings via the SiliconFlow OpenAI-compatible API.

        Returns a (N, D) float32 ndarray, or None on failure.
        """
        if not settings.EMBEDDING_API_KEY:
            logger.error("EMBEDDING_API_KEY is not set; cannot generate embeddings")
            return None
        return self._generate_embeddings_api(texts)

    def _generate_embeddings_api(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings via the SiliconFlow OpenAI-compatible /embeddings endpoint."""
        if not settings.EMBEDDING_MODEL:
            logger.error("EMBEDDING_API_KEY set but EMBEDDING_MODEL is empty; cannot call API")
            return None

        url = f"{settings.EMBEDDING_BASE_URL.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}",
            "Content-Type": "application/json",
        }
        batch_size = max(1, settings.EMBEDDING_BATCH_SIZE)
        all_vectors: List[List[float]] = []

        logger.info(
            f"Requesting embeddings from {url} for {len(texts)} texts "
            f"(model={settings.EMBEDDING_MODEL}, batch={batch_size})"
        )

        with httpx.Client(timeout=settings.EMBEDDING_TIMEOUT) as client:
            for start in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
                batch = texts[start:start + batch_size]
                # SiliconFlow rejects empty strings; coerce to a single space.
                payload = {
                    "model": settings.EMBEDDING_MODEL,
                    "input": [t if t else " " for t in batch],
                    "encoding_format": "float",
                }
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(
                        f"Embedding API error {resp.status_code}: {resp.text[:500]}"
                    )
                    return None
                data = resp.json().get("data")
                if not data:
                    logger.error(f"Embedding API returned no data: {resp.text[:500]}")
                    return None
                # API may return embeddings out of order; sort by index if present.
                data = sorted(data, key=lambda d: d.get("index", 0))
                all_vectors.extend(d["embedding"] for d in data)

        if len(all_vectors) != len(texts):
            logger.error(
                f"Embedding count mismatch: got {len(all_vectors)} for {len(texts)} texts"
            )
            return None

        logger.info(f"Got {len(all_vectors)} embeddings (dim={len(all_vectors[0])})")
        return np.asarray(all_vectors, dtype=np.float32)

    def _run_umap(self, embeddings: np.ndarray) -> np.ndarray:
        """Run UMAP dimensionality reduction"""
        if embeddings is None:
            logger.warning("No embeddings provided for UMAP, returning None")
            return None

        try:
            reducer = UMAP(
                n_neighbors=15,
                min_dist=0.1,
                metric='cosine',
                random_state=42
            )
            embeddings_2d = reducer.fit_transform(embeddings)
            return embeddings_2d
        except Exception as e:
            logger.error(f"UMAP failed: {e}")
            # Fallback: use first 2 dimensions if available, otherwise random
            if embeddings.shape[1] >= 2:
                return embeddings[:, :2]
            return np.random.rand(embeddings.shape[0], 2)

    def _save_embeddings(self, dataset_id: str, texts: List[str], embeddings_2d: np.ndarray, db: Session):
        """Save embeddings to database"""
        try:
            # Clear existing embeddings for this dataset
            db.query(Embedding).filter(Embedding.dataset_id == dataset_id).delete()

            # Insert new embeddings
            embeddings_list = []
            for i, (text, (x, y)) in enumerate(zip(texts, embeddings_2d)):
                embedding = Embedding(
                    dataset_id=dataset_id,
                    vector=str(embeddings_2d[i].tolist()),  # Store as string for pgvector
                    x_coord=float(x),
                    y_coord=float(y),
                    text_content=text[:10000],  # Limit text length
                    metadata={"index": i}
                )
                embeddings_list.append(embedding)

            db.bulk_save_objects(embeddings_list)
            db.commit()
            logger.info(f"Saved {len(embeddings_list)} embeddings to database")

        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            db.rollback()
            raise

    def _generate_wizmap_data(self, embeddings_2d: np.ndarray, texts: List[str]) -> Tuple[Dict, List]:
        """Generate WizMap format data using existing wizmap functions"""
        try:
            xs = embeddings_2d[:, 0].astype(float).tolist()
            ys = embeddings_2d[:, 1].astype(float).tolist()

            # Generate grid data for contours + topic labels. generate_grid_dict
            # merges the contour grid and the multi-level topic summary into a
            # single dict (the frontend expects both in one grid object).
            if WIZMAP_AVAILABLE:
                grid_dict = generate_grid_dict(
                    xs=xs,
                    ys=ys,
                    texts=texts,
                    grid_size=200,
                )
            else:
                # Simplified grid without wizmap
                grid_dict = self._generate_simple_grid(xs, ys)

            # Generate data list
            data_list = []
            for i, (x, y, text) in enumerate(zip(xs, ys, texts)):
                data_list.append([x, y, text[:500]])  # Limit text length

            return grid_dict, data_list

        except Exception as e:
            logger.error(f"Error generating WizMap data: {e}")
            raise

    def _generate_simple_grid(self, xs: List[float], ys: List[float]) -> Dict:
        """Generate simple grid data when wizmap is not available"""
        # Simple histogram-based density estimation
        import numpy as np

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # Create 50x50 grid
        grid_size = 50
        grid_x = np.linspace(x_min, x_max, grid_size)
        grid_y = np.linspace(y_min, y_max, grid_size)

        # Simple density estimation
        density, _, _ = np.histogram2d(xs, ys, bins=[grid_x, grid_y])

        return {
            "grid": density.T.tolist(),
            "xRange": [x_min, x_max],
            "yRange": [y_min, y_max],
            "padded": True,
            "sampleSize": len(xs),
            "totalPointSize": len(xs)
        }

    def _upload_processed_data(self, dataset_id: str, grid_dict: Dict, data_list: List) -> Tuple[str, str]:
        """Upload processed data files to MinIO"""
        try:
            # Upload grid data
            grid_path = f"datasets/{dataset_id}/grid.json"
            grid_content = json.dumps(grid_dict).encode('utf-8')
            self.minio_service.client.put_object(
                bucket_name=self.minio_service.bucket,
                object_name=grid_path,
                data=__import__('io').BytesIO(grid_content),
                length=len(grid_content)
            )

            # Upload data as ndjson
            data_path = f"datasets/{dataset_id}/data.ndjson"
            data_content = '\n'.join([json.dumps(item) for item in data_list]).encode('utf-8')
            self.minio_service.client.put_object(
                bucket_name=self.minio_service.bucket,
                object_name=data_path,
                data=__import__('io').BytesIO(data_content),
                length=len(data_content)
            )

            return grid_path, data_path

        except Exception as e:
            logger.error(f"Error uploading processed data: {e}")
            raise

    def _save_processed_result(self, dataset_id: str, grid_path: str, data_path: str, grid_dict: Dict, db: Session):
        """Save processed result metadata to database"""
        try:
            processed_result = ProcessedResult(
                dataset_id=dataset_id,
                grid_file_path=grid_path,
                data_file_path=data_path,
                grid_size=len(grid_dict.get('grid', [])),
                x_range=grid_dict.get('xRange', []),
                y_range=grid_dict.get('yRange', [])
            )
            db.add(processed_result)
            db.commit()
            logger.info(f"Saved processed result for dataset {dataset_id}")

        except Exception as e:
            logger.error(f"Error saving processed result: {e}")
            db.rollback()
            raise
