import json

from celery import Celery
from vosk import Model, KaldiRecognizer

from .database import SessionLocal
from .models import RecognitionResult

app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/1'
)

model = Model("vosk-model")


@app.task
def process_audio(audio_path: str):
    try:
        # Чтение аудио как сырых PCM-данных
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        rec = KaldiRecognizer(model, 16000)  # Укажите явно частоту дискретизации
        result = []

        # Передаем данные порциями по 4000 сэмплов
        chunk_size = 4000
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if rec.AcceptWaveform(chunk):
                partial = json.loads(rec.Result())
                result.append(partial.get("text", ""))

        # Финализируем результат
        final = json.loads(rec.FinalResult())
        text = " ".join(result + [final.get("text", "")])

        # Сохранение в БД
        db = SessionLocal()
        db.add(RecognitionResult(audio_path=audio_path, text=text))
        db.commit()
        db.close()

        return {"text": text}
    except Exception as e:
        return {"text": "", "error": str(e)}

