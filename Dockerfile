FROM --platform=linux/arm64 python:3.9.0

RUN apt-get update -y
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY app app
RUN wget -P /app/app/artifacts/big-lama
RUN wget -P /app/app/artifacts/sd2
COPY requirements.txt .

RUN pip install -r requirements.txt --default-timeout=100

RUN flake8 app/main.py
RUN flake8 app/schemas
RUN flake8 app/tests
RUN pytest app/tests

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]