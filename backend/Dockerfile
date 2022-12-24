FROM python:3.7-slim

WORKDIR /app

COPY ../backend .

RUN pip3 install -r requirements.txt --no-cache-dir


CMD ["gunicorn", "foodrgram.wsgi:application", "--bind", "0:8000"]