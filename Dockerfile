
# syntax=docker/dockerfile:1
FROM python:3.10.1-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["gunicorn", "--bind=0.0.0.0:8050", "app:server"]
#CMD ["python", "app.py"]