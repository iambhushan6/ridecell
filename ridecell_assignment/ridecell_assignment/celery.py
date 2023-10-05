import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ridecell_assignment.settings")

app = Celery("ridecell_assignment")
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace='CELERY')


# Beat Settings
# Load task modules from all registered Django apps.
app.conf.beat_schedule = {
    "fetch-youtube-video-data": {
        "task" : "main.tasks.scheduled_task_fetch_youtube_video_data",
        "schedule" : 60.0,
        "args" : ()
    }
}
app.autodiscover_tasks()


