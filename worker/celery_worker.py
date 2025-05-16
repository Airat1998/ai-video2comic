import os
import sys
from celery import Celery
from worker.stylizer import stylize_video
from pdf.comic_maker import make_comic

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

celery_app = Celery(
    "worker", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)


@celery_app.task(name="worker.process_video")
def process_video(video_path):
    frames = stylize_video(video_path)
    return make_comic(frames, video_path)
