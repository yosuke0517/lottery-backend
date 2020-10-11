FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install --upgrade pip \
    -r requirements.txt && \
    pip install psycopg2 \
    pandas \
    selenium \
    beautifulsoup4 \
    sqlalchemy
ADD . /app/a