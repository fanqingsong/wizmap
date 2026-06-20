from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class DatasetStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: DatasetStatus
    processing_progress: float = 0.0
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    total_records: Optional[int] = None

    model_config = {'from_attributes': True}

    # In Pydantic v2, UUID should automatically serialize to string when using from_attributes
    # If this doesn't work, we'll need to manually convert in the endpoint


class DatasetList(BaseModel):
    datasets: List[DatasetResponse]
    total: int


class FileUploadResponse(BaseModel):
    dataset_id: str
    message: str
    status: str

    model_config = {'from_attributes': True}

    @field_serializer('dataset_id')
    def serialize_dataset_id(self, value: uuid.UUID) -> str:
        return str(value)


class ProcessingStatus(BaseModel):
    dataset_id: str
    status: str
    progress: float
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    estimated_remaining_seconds: Optional[int] = None

    model_config = {'from_attributes': True}

    @field_serializer('dataset_id')
    def serialize_dataset_id(self, value: uuid.UUID) -> str:
        return str(value)


class PointData(BaseModel):
    x: float
    y: float
    text: str


class GridData(BaseModel):
    grid: List[List[float]]
    x_range: List[float]
    y_range: List[float]
    sample_size: int
    total_point_size: int
