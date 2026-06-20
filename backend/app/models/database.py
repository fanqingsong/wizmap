from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey, Enum, JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class DatasetStatus(enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.UPLOADING)
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)
    total_records = Column(Integer, nullable=True)

    # Processing metadata
    processing_progress = Column(Float, default=0.0)
    current_step = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    embeddings = relationship("Embedding", back_populates="dataset", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="dataset", cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    # Vector storage using pgvector
    vector = Column(String, nullable=False)  # Will be converted to pgvector type

    # 2D projection coordinates
    x_coord = Column(Float, nullable=False)
    y_coord = Column(Float, nullable=False)

    # Original text content
    text_content = Column(Text, nullable=False)

    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    meta = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="embeddings")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    # Job tracking
    celery_task_id = Column(String(255), unique=True, nullable=True)
    status = Column(String(50), default="pending")
    progress = Column(Float, default=0.0)
    current_step = Column(String(100), nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="processing_jobs")


class ProcessedResult(Base):
    __tablename__ = "processed_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)

    # Result file paths in MinIO
    grid_file_path = Column(String(512), nullable=False)
    data_file_path = Column(String(512), nullable=False)

    # Metadata
    grid_size = Column(Integer, nullable=True)
    x_range = Column(JSON, nullable=True)  # [min, max]
    y_range = Column(JSON, nullable=True)  # [min, max]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
