#
# To build:
# > sudo docker build -t rest .
#
# to start as daemon with port 9080 of api exposed as 9080 on host
# and host's directory ${PROJECT_DIR} mounted as /rest/project
#
# > sudo docker run -p 9080:9080 -tid -v ${PROJECT_DIR}:/rest/project rest
#

FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 627220E7
RUN echo 'deb http://archive.scrapy.org/ubuntu scrapy main' | tee /etc/apt/sources.list.d/scrapy.list

RUN apt-get update && \
    apt-get install -y python python-dev python-pip \
    libffi-dev libxml2-dev libxslt1-dev zlib1g-dev libssl-dev

RUN mkdir -p /galaxy/src /galaxy/project
RUN mkdir -p /var/log/galaxy

WORKDIR /galaxy/src

ADD requirements.txt /galaxy/src/requirements.txt
RUN pip install -r requirements.txt

ADD . /galaxy/src
RUN pip install /galaxy/src

WORKDIR /galaxy/project

ENTRYPOINT ["galaxy", "-i 0.0.0.0"]

EXPOSE 9080
