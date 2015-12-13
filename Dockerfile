FROM mopsalarm/python-base:3.5
MAINTAINER Mopsalarm

RUN apt-get update && apt-get install -y curl tar coreutils xz-utils
RUN curl http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz \
    | tar xJ --no-anchored --strip-components=1 -C /usr/bin -i ffmpeg

EXPOSE 5000

CMD python -u -m bottle -s cherrypy -b 0.0.0.0:5000 thumby
