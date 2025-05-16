#  AI Video Comic PDF Generator

FastAPI + Celery + StableDiffusion + ControlNet + BLIP = готовый комикс из видео

##  Стек

- FastAPI — загрузка видео
- Celery — воркер с GPU
- StableDiffusion + ControlNet — стилизация
- BLIP — текстовое описание сцен
- ReportLab — PDF-комикс
- Redis — брокер задач

##  Запуск

docker-compose up --build
# Trigger CI/CD
