FROM python:3.7

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install dialog apt-utils -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code
ENV APP_ROOT /code

WORKDIR /code
	
COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock
RUN pip install pipenv && pipenv install --system

COPY . /code/

RUN python /code/setup.py build
RUN python /code/setup.py install