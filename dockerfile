FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPYCACHEPREFIX=/tmp

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8080", "src.main:app"]
