FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r requirements.txt



