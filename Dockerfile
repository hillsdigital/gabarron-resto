# Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dependencias del sistema necesarias para psycopg2 y build
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para cachear la instalación
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "gabarronresto.wsgi:application", "--bind", "0.0.0.0:8000"]
