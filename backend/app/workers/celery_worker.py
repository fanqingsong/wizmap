from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "wizmap_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.celery_worker"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000
)


@celery_app.task(name="app.workers.celery_worker.process_dataset_task")
def process_dataset_task(dataset_id: str, file_path: str):
    """
    Celery task for processing datasets asynchronously
    This task runs the complete ML pipeline: text → embeddings → UMAP → WizMap format
    """
    from app.core.database import SessionLocal
    from app.services.processing_service import ProcessingService
    import logging

    logger = logging.getLogger(__name__)

    db = None
    try:
        # Create new database session for this task
        db = SessionLocal()

        # Initialize processing service
        processing_service = ProcessingService()

        # Process the dataset
        logger.info(f"Starting processing for dataset: {dataset_id}")
        result = processing_service.process_dataset(dataset_id, db)

        if result:
            logger.info(f"Successfully processed dataset: {dataset_id}")
        else:
            logger.error(f"Failed to process dataset: {dataset_id}")

        return {"dataset_id": dataset_id, "success": result}

    except Exception as e:
        logger.error(f"Error in processing task for dataset {dataset_id}: {e}")
        raise
    finally:
        if db is not None:
            db.close()
