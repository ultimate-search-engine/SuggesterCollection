FROM python:3.10
COPY ./Suggester /algorithm
WORKDIR /algorithm
RUN pip install --requirement /algorithm/requirements.txt
RUN touch .env