from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime

from app.core.database import get_db
from app.models.database import Dataset, DatasetStatus, ProcessedResult
from app.schemas.schemas import DatasetCreate, DatasetResponse, FileUploadResponse, ProcessingStatus
from app.core.config import settings
from app.services.minio_service import MinioService
from app.services.processing_service import ProcessingService

router = APIRouter()

# Initialize services
minio_service = MinioService()
processing_service = ProcessingService()


@router.post("/", response_model=FileUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Upload a text file and create a dataset for processing"""

    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_FILE_EXTENSIONS}"
        )

    # Create dataset record
    dataset = Dataset(
        name=name or file.filename,
        description=description,
        status=DatasetStatus.UPLOADING
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    try:
        # Upload file to MinIO
        file_path = f"datasets/{dataset.id}/{file.filename}"
        await minio_service.upload_file(file, file_path)

        # Update dataset with file info
        dataset.file_path = file_path
        dataset.status = DatasetStatus.PROCESSING
        db.commit()

        # Dispatch the async processing task.
        # Local import to avoid importing the Celery app (and its broker
        # connection) at module load time.
        try:
            from app.workers.celery_worker import process_dataset_task
            process_dataset_task.delay(str(dataset.id), file_path)
        except Exception as e:
            # Fall back to synchronous processing if the broker is unavailable,
            # so uploads still complete in development.
            processing_service.process_dataset(str(dataset.id), db)

        return FileUploadResponse(
            dataset_id=str(dataset.id),
            message="Dataset uploaded successfully and processing started",
            status="processing"
        )

    except Exception as e:
        dataset.status = DatasetStatus.FAILED
        dataset.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all datasets"""
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()

    # Manually convert UUIDs to strings to avoid Pydantic validation issues
    result = []
    for dataset in datasets:
        dataset_dict = {
            'id': str(dataset.id),
            'name': dataset.name,
            'description': dataset.description,
            'status': dataset.status.value,
            'processing_progress': dataset.processing_progress,
            'current_step': dataset.current_step,
            'error_message': dataset.error_message,
            'created_at': dataset.created_at,
            'updated_at': dataset.updated_at,
            'completed_at': dataset.completed_at,
            'total_records': dataset.total_records
        }
        result.append(DatasetResponse(**dataset_dict))

    return result


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get a specific dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Manually convert UUID to string to avoid Pydantic validation issues
    dataset_dict = {
        'id': str(dataset.id),
        'name': dataset.name,
        'description': dataset.description,
        'status': dataset.status.value,
        'processing_progress': dataset.processing_progress,
        'current_step': dataset.current_step,
        'error_message': dataset.error_message,
        'created_at': dataset.created_at,
        'updated_at': dataset.updated_at,
        'completed_at': dataset.completed_at,
        'total_records': dataset.total_records
    }
    return DatasetResponse(**dataset_dict)


@router.get("/{dataset_id}/status", response_model=ProcessingStatus)
async def get_dataset_status(dataset_id: str, db: Session = Depends(get_db)):
    """Get processing status of a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return ProcessingStatus(
        dataset_id=str(dataset.id),
        status=dataset.status.value,
        progress=dataset.processing_progress,
        current_step=dataset.current_step,
        error_message=dataset.error_message
    )


@router.get("/{dataset_id}/data")
async def get_dataset_data(dataset_id: str, db: Session = Depends(get_db)):
    """Get processed point data for visualization"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.status != DatasetStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset not ready. Current status: {dataset.status.value}"
        )

    # Get processed result
    processed_result = db.query(ProcessedResult).filter(
        ProcessedResult.dataset_id == dataset_id
    ).first()

    if not processed_result:
        raise HTTPException(status_code=404, detail="Processed data not found")

    # Stream data from MinIO. Return raw bytes as a Response so FastAPI does
    # not JSON-encode (and thus double-encode) the already-serialized file.
    data = await minio_service.get_file(processed_result.data_file_path)
    return Response(content=data, media_type="application/x-ndjson")


@router.get("/{dataset_id}/grid")
async def get_dataset_grid(dataset_id: str, db: Session = Depends(get_db)):
    """Get processed grid data for visualization"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.status != DatasetStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset not ready. Current status: {dataset.status.value}"
        )

    # Get processed result
    processed_result = db.query(ProcessedResult).filter(
        ProcessedResult.dataset_id == dataset_id
    ).first()

    if not processed_result:
        raise HTTPException(status_code=404, detail="Processed data not found")

    # Stream data from MinIO. Return raw bytes as a Response so FastAPI does
    # not JSON-encode (and thus double-encode) the already-serialized file.
    grid = await minio_service.get_file(processed_result.grid_file_path)
    return Response(content=grid, media_type="application/json")


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete a dataset and all associated data"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Delete files from MinIO
        if dataset.file_path:
            await minio_service.delete_file(dataset.file_path)

        # Delete processed results
        processed_results = db.query(ProcessedResult).filter(
            ProcessedResult.dataset_id == dataset_id
        ).all()

        for result in processed_results:
            await minio_service.delete_file(result.grid_file_path)
            await minio_service.delete_file(result.data_file_path)
            db.delete(result)

        # Delete dataset (cascade will handle embeddings and jobs)
        db.delete(dataset)
        db.commit()

        return {"message": "Dataset deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")