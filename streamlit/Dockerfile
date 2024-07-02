FROM python:3.9 AS base 

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt 

COPY . .

CMD ["streamlit", "run", "./src/main.py"]
