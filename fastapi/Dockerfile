FROM python:3.9 AS base 

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt 

# RUN pip install psycopg[binary,pool]

COPY . .

RUN python -m pytest ./src/tests

CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
