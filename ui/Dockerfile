# ui/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./Register.py /app/Register.py
COPY ./pages /app/pages

EXPOSE 8501

CMD ["streamlit", "run", "Register.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
