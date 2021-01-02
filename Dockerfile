FROM python:3.7.7-slim-stretch
LABEL application="Pynance : A Portfolio Management Application"
LABEL maintainers=["Grant Moore <chinchalinchin@gmail.com>"]
LABEL version="prototype-1.0.0"
LABEL description="A financial application for managing portfolios"

RUN apt update -y && apt-get -y install libgl1-mesa-glx ffmpeg libsm6 libxext6 
WORKDIR /home/
RUN mkdir ./app && mkdir ./cache && mkdir ./static && mkdir ./gui && mkdir ./util

COPY /requirements.txt /home/requirements.txt
RUN pip install -r requirements.txt

COPY /app /home/app
COPY /cache /home/cache
COPY /static /home/static
COPY /gui /home/gui
COPY /util /home/util

VOLUME /home/cache /home/static

WORKDIR /home
COPY /main.py /home/main.py

ENTRYPOINT [ "python", "./main.py" ]
CMD [ "-help" ]
