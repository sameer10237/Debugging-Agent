"""Celery task queue for background jobs."""

from celery import Celery, Task
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    "debugging_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


class CallbackTask(Task):
    """Task with callback support."""

    def on_success(self, retval, task_id, args, kwargs):
        """Success callback."""
        logger.info(f"Task {task_id} succeeded")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry callback."""
        logger.warning(f"Task {task_id} retrying: {str(exc)}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback."""
        logger.error(f"Task {task_id} failed: {str(exc)}")


@celery_app.task(bind=True, base=CallbackTask)
def run_debugging_workflow(self, execution_id: str, project_id: str):
    """
    Run debugging workflow asynchronously.
    
    Args:
        execution_id: Execution UUID
        project_id: Project UUID
    """
    try:
        logger.info(f"Starting workflow for execution {execution_id}")
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"step": "Initializing workflow"})
        
        # Import here to avoid circular imports
        import asyncio
        from app.agents import create_orchestrator
        
        # Create orchestrator
        orchestrator = create_orchestrator()
        
        # Prepare workflow
        workflow_config = {
            "initial_state": {
                "execution_id": execution_id,
                "project_id": project_id,
                "test_framework": "pytest",
            },
            "steps": [
                {"agent": "testing_agent", "update_state": True},
                {"agent": "debugging_agent", "update_state": True},
                {"agent": "coding_agent", "update_state": True},
                {"agent": "architect_agent", "update_state": True},
                {"agent": "project_manager_agent", "update_state": True},
            ]
        }
        
        # Execute workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                orchestrator.execute_workflow(workflow_config)
            )
        finally:
            loop.close()
        
        logger.info(f"Workflow completed for execution {execution_id}")
        
        return {
            "execution_id": execution_id,
            "status": "completed",
            "results": results,
        }
        
    except Exception as exc:
        logger.error(f"Workflow failed: {str(exc)}")
        
        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries), max_retries=3)


@celery_app.task
def check_execution_status(execution_id: str):
    """Check the status of an execution."""
    logger.info(f"Checking status for execution {execution_id}")
    # Implementation would check database
    return {"execution_id": execution_id, "status": "pending"}


@celery_app.task
def cleanup_old_executions(days: int = 30):
    """Clean up old execution records."""
    logger.info(f"Cleaning up executions older than {days} days")
    # Implementation would delete old records
    return {"deleted": 0}


# Task monitoring functions
def get_task_status(task_id: str):
    """Get the status of a Celery task."""
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "state": result.state,
        "result": result.result if result.ready() else None,
        "progress": result.info.get("progress") if isinstance(result.info, dict) else None,
    }


def revoke_task(task_id: str):
    """Revoke a Celery task."""
    celery_app.control.revoke(task_id, terminate=True)
    logger.info(f"Task {task_id} revoked")


# Periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'check-executions': {
        'task': 'app.celery_app.check_execution_status',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-data': {
        'task': 'app.celery_app.cleanup_old_executions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
