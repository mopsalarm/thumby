from python:2-onbuild
MAINTAINER Mopsalarm

RUN apt-get update && apt-get install -y --force-yes libav-tools && apt-get clean

# images are placed at /usr/src/app/images
CMD python thumby.py

EXPOSE 5000

