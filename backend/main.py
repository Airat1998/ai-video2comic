import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from worker.celery_worker import celery_app

app = FastAPI()

DATA_DIR = "/app/data"
HOST = "http://46.17.99.9:8000"


@app.post("/convert/")
async def convert(video: UploadFile = File(...)):
    save_path = os.path.join(DATA_DIR, video.filename)
    with open(save_path, "wb") as f:
        f.write(await video.read())

    task = celery_app.send_task("worker.process_video", args=[save_path])
    return {"task_id": task.id}


@app.get("/status/{task_id}")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.successful():
        pdf_path = result.result
        filename = os.path.basename(pdf_path)
        response["download_url"] = f"{HOST}/download/{filename}"

    return response


@app.get("/download/{filename}")
async def download(filename: str):
    path = f"/app/data/{filename}"
    print(f"[DOWNLOAD] Try to access file: {path}")
    if not os.path.exists(path):
        print(f"[DOWNLOAD] File NOT FOUND: {path}")
        raise HTTPException(status_code=404, detail="Файл не найден")
    print(f"[DOWNLOAD] File FOUND: {path}")
    return FileResponse(path, media_type="application/pdf", filename=filename)
