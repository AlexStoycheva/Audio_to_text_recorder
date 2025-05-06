#!/usr/bin/python3
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import speech_recognition as sr
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def get_home():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/recognize")
async def recognize_audio(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file.file) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return {"text": text}
    except sr.UnknownValueError:
        return {"text": ""}
    except sr.RequestError as e:
        return {"error": str(e)}

@app.post("/live_recognition")
async def live_recognition(r):
    while(1):
        try:
            with sr.Microphone() as source:

                r.adjust_for_ambient_noise(source, duration=0.2)

                audio = r.listen(source, phrase_time_limit=5)
                text = r.recognize_google(audio)

                return text
        
        except sr.RequestError as re:
            print("Could not request result: {}".format(re))

        except sr.UnknownValueError:
            print("Unknown error occured!")
        
        except:
            print("Something went wrong!")

def output_text(text):
    with open("current_output.txt", "w") as curr_text:
        curr_text.write(text)
        curr_text.write("\n")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
