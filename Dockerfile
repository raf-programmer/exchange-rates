# pull official base image
FROM python:3.8.12-slim-buster

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app   #  going to create a group and a user.


# Next, we will move forward and create our app directory where we will copy our code.
ENV HOME=/home/app
ENV APP_HOME=/home/app/code
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod


# Following up, we will install system and python dependencies.
RUN apt-get update \
  && apt-get -y install netcat gcc libpq-dev \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -U setuptools
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN apt-get update && apt-get install -y curl

# After that I will copy the entire code, change ownership and finally run the gunicorn process at port 5000.
# add app
COPY . .

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run gunicorn
CMD gunicorn --bind 0.0.0.0:5000 main:app -k uvicorn.workers.UvicornWorker