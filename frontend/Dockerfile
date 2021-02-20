FROM nginx:latest

# VERSION CONTROLS
ENV NODE_VERSION=14
ENV ANGULAR_VERSION=11

# DEFAULT USER & GROUP
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance

# OS DEPENDENCIES
RUN apt-get update -y && apt-get install -y curl moreutils

# FRONTEND DEPENDENCIES
RUN curl -sL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs
RUN npm install -g @angular/cli@${ANGULAR_VERSION}

# NGINX CONFIGURATION
COPY /server/nginx.conf /etc/nginx/nginx.conf
COPY /server/mime.types /etc/nginx/mime.types

# FRONTEND CONFIGURATION
RUN mkdir /home/build/ && mkdir /home/frontend/
COPY /pynance-web/ /home/frontend/
WORKDIR /home/frontend/
RUN npm install
RUN ng build --prod --output-hashing none

# PERMISSION CONFIGURATOIN
RUN chown -R pynance:pyadmin /home/frontend/ /home/build/ /etc/nginx/nginx.conf /var/cache/nginx/ /var/run/ /var/log/nginx/
RUN chmod -R 770 /home/frontend/ 
RUN chmod -R 770 /home/build/

# ENTRYPOINT CONFIGURATION
EXPOSE 8080
RUN mkdir /home/scripts/
COPY /scripts/web-entrypoint.sh /home/scripts/web-entrypoint.sh
COPY /scripts/logging.sh /home/scripts/util/logging.sh
USER pynance
CMD [ "bash", "/home/scripts/web-entrypoint.sh" ]