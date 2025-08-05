FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias necesarias para compilar e instalar psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    pkg-config \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

CMD ["gunicorn", "gabarronresto.wsgi:application", "--bind", "0.0.0.0:8000"]
