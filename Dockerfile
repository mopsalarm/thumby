FROM gliderlabs/python-runtime:3.4
MAINTAINER Mopsalarm

RUN apk --update add ffmpeg coreutils

EXPOSE 5000

CMD /env/bin/python thumby.py
