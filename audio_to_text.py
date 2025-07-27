from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydub import AudioSegment

import os
import io
import tempfile
import speech_recognition as sr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
def serve_home():
    return FileResponse("templates/index.html")

@app.post("/recognize/chunk")
async def recognize_chunk(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()

    # Read uploaded bytes
    data = await file.read()

    # Convert from WebM/OGG to WAV
    try:
        audio = AudioSegment.from_file(io.BytesIO(data), format="webm")  # or "ogg"
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
    except Exception as e:
        return {"error": f"Could not convert audio: {e}"}

    # Transcribe
    try:
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    except Exception as e:
        return {"error": str(e)}

    return {"text": text}

@app.post("/recognize/upload")
async def recognize_upload(file: UploadFile = File(...), chunk_length=60):
    recognizer = sr.Recognizer()
    result = []

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(await file.read())
        mp3_path = tmp.name

    # Convert to WAV using pydub
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    audio.export(wav_path, format="wav")

    # Transcribe the WAV
    with sr.AudioFile(wav_path) as source:
        duration = source.DURATION
        offset = 0

        while offset < duration:
            audio_data = recognizer.record(source, duration=59)

            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError as e:
                return JSONResponse(status_code=500, content={"error": str(e)})
            
            result.append(text)
            offset += chunk_length

    # Return .txt file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
        f.write(" ".join(result))
        temp_txt = f.name

    # Clean up temporary files
    os.remove(mp3_path)
    os.remove(wav_path)

    return FileResponse(temp_txt, media_type="text/plain", filename="transcription.txt")
