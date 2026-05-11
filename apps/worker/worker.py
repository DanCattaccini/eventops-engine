from eventops.tasks import celery_app, process_event  # noqa: F401 – re-export for Celery discovery

__all__ = ["celery_app"]
