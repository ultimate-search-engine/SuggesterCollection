FROM python:3.10
COPY ./Suggester/. /app
WORKDIR /app
RUN pip install --requirement /app/requirements.txt
RUN touch .env