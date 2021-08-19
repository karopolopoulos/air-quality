FROM python:3.8

WORKDIR /air-quality

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

CMD ["python", "src/main.py"]