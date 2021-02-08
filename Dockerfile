FROM python:latest

# DEFAULT USER & GROUP
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance

COPY /app/ /home/app/
COPY /server/ /home/server/
COPY /scripts/ /home/scripts/
COPY /util/ /home/util/
COPY /requirements.txt /home/requirements

RUN pip install -r requirements.txt

RUN chown -R pynance:pyadmin /home/app/ /home/server/ /home/util/ /home/scripts/
RUN chmod -R 770 /home/app/ 
RUN chmod -R 770 /home/server/

WORKDIR /home/scripts/
ENTRYPOINT [ "pynance" ]
CMD [ "--help" ]
