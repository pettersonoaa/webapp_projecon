# Base Image
FROM python:3.8

# create and set working directory
RUN mkdir /app
WORKDIR /app

# Add current directory code to working directory
ADD . /app/

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive 

# set project environment variables
# grab these via the Python os.environ
# these are 100% optional here
# $PORT is set by Heroku
ENV PORT=8888
#ENV DEBUG=0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install environment and project dependencies
RUN pip3 install --upgrade pip 
RUN pip3 install pipenv
RUN pipenv install --skip-lock --system --dev

# Expose is NOT supported by Heroku
# EXPOSE 8888
CMD gunicorn projecon.wsgi:application --bind 0.0.0.0:$PORT