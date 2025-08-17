FROM python:3.12-slim

ENV MONGO_DB_USERNAME=admin \
    MONGO_DB_PWD=password

RUN apt-get update && apt-get install -y \
    build-essential \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/app1

EXPOSE 3001

CMD ["uvicorn", "audio_to_text:app", "--reload", "--port", "3001"]