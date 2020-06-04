FROM ubuntu:18.04

RUN apt update \
    && apt upgrade -y

RUN apt update \
    && apt upgrade -y \
    && apt install -y python3 python3-pip build-essential libssl-dev libffi-dev python3-dev

WORKDIR /air-quality
COPY requirements.txt .
COPY .env .
COPY certs certs
COPY lib lib

RUN pip3 install -r requirements.txt

CMD ["python3", "lib/main.py"]