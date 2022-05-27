FROM python:3.9-slim-buster

WORKDIR /app

# 👇
COPY requirements.txt ./
RUN pip install -r requirements.txt
# 👆

COPY *.py .
COPY mqtt.conf .

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-dev}

CMD [ "python", "./send2hec.py"]