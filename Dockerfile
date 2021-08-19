FROM python:3.8

RUN apt update \
  && apt upgrade -y \
  && apt install -y cmake

WORKDIR /air-quality

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

CMD ["python", "src/main.py"]