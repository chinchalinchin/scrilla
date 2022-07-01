FROM circleci/python:latest

WORKDIR /home/
RUN sudo apt-get update -y && \
    sudo apt-get install -y libxkbcommon-x11-0 \
                        x11-utils \
                        libopengl0 \
                        libegl1-mesa \
                        xvfb \
                        ffmpeg \
                        libsm6 \
                        libxext6

# TODO: install deepsource cli

# do not need to install requirements, as it will be quicker to cache them on circleci build servers