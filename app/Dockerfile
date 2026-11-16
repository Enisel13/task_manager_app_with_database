FROM python:3.11-slim

WORKDIR /app

ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py .
COPY templates/ templates/

EXPOSE 5001

CMD ["python", "app.py"] 
