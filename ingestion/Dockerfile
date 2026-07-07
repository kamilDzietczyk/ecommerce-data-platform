FROM python:3.11-slim

WORKDIR /usr/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/usr/app

CMD ["tail", "-f", "/dev/null"]