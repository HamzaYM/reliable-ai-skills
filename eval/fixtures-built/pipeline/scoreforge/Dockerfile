FROM python:3.12-slim
WORKDIR /srv
COPY app/ /srv/app/
COPY jobs/ /srv/jobs/
COPY ops/*.py /srv/ops/
RUN pip install pyyaml
CMD ["python3", "-m", "app.scoring_service"]
