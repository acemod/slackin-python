FROM ubuntu:14.04
MAINTAINER Felix Wiegand <koffeinflummi@gmail.com>

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip

ADD . /opt/slackin-python
WORKDIR /opt/slackin-python

RUN python3 setup.py install

EXPOSE 80
CMD slackin -p 80 $SLACKIN_SUBDOMAIN $SLACKIN_APITOKEN
