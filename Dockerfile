from yaronr/debian-wheezy
MAINTAINER Mopsalarm

RUN apt-get update && apt-get install -y --force-yes libav-tools python-pip

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD start.sh /app/start.sh
ADD thumby.py /app/thumby.py

CMD /bin/sh /app/start.sh

EXPOSE 5000

