FROM python:3.10.11

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
   pip install --default-timeout=100 -r /app/requirements.txt

CMD [ "python3", "/app/main.py"]