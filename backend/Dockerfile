FROM python:3.12.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código de Django no se copia: se monta en runtime con -v sobre /app.

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
