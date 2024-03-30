FROM python:3.11-slim-bookworm AS python-base

FROM python-base AS base
WORKDIR /data_feed/
COPY ./feed.py ./requirements.txt ./
RUN apt-get update && apt-get upgrade -y \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python", "feed.py"]
