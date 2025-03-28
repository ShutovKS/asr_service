import os
import uuid

from fastapi import FastAPI, UploadFile
from pydub import AudioSegment

from .database import init_db
from .tasks import process_audio

app = FastAPI()


@app.on_event("startup")
async def startup():
    init_db()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_path, format="wav")


@app.post("/recognize")
async def recognize_audio(file: UploadFile):
    # Конвертация в нужный формат
    converted_path = f"converted_{uuid.uuid4()}.wav"
    convert_to_wav(file.file, converted_path)

    task = process_audio.delay(converted_path)
    return {"task_id": task.id}


@app.get("/result/{task_id}")
def get_result(task_id: str):
    task = process_audio.AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"status": "completed", "result": task.result}
    else:
        return {"status": task.state}
