FROM python:3.11-slim

WORKDIR /usr/app

COPY ai_assistant/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH=/usr/app

CMD ["uvicorn", "ai_assistant.app.main:app", "--host", "0.0.0.0", "--port", "8000"]