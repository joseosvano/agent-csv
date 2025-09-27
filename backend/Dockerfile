FROM python:3.11.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

EXPOSE 8000

# Comando para rodar o servidor usando a porta do container
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]
