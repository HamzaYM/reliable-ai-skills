FROM python:3.12-slim
WORKDIR /srv
COPY . /srv
RUN pip install -r requirements.txt
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
