FROM circleci/python:latest

RUN apt-get update -y && \
    apt-get install -y libxkbcommon-x11-0 \
                        x11-utils \
                        libopengl0 \
                        libegl1-mesa && \
    curl https://deepsource.io/cli | sh

COPY requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt