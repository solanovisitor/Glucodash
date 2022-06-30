FROM python:slim-bullseye

COPY . /glucodash

RUN apt update \
    && apt -y install build-essential libffi-dev \
    && cd /glucodash \
    && MAKEFLAGS="-j$(nproc --all --ignore=1)" pip install --no-cache-dir -r requirements.txt \
    && apt -y purge build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8501/tcp

WORKDIR /glucodash

CMD [ "streamlit", "run", "app.py" ]
