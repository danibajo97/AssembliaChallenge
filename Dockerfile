FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD ["gunicorn", "AssembliaChallenge.wsgi:application", "--bind", "0.0.0.0:8000"]
