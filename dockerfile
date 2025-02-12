FROM python:3.10-slim

WORKDIR /app

COPY . .

COPY requirements.txt /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

CMD python -u run.py