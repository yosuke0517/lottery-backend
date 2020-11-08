FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/