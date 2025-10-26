FROM python:3.13-slim
WORKDIR /app

COPY ./src ./src
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
