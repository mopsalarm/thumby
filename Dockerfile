FROM gliderlabs/python-runtime:3.4
MAINTAINER Mopsalarm

RUN curl http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz \
    | xz -d \
    | tar xC /usr/bin --strip-components=1 \
    && rm /usr/bin/ffserver \
    && rm /usr/bin/ffprobe \
    && rm /usr/bin/ffmpeg-10bit

RUN apk del tar xz curl

EXPOSE 5000

WORKDIR /data
CMD /env/bin/python /app/thumby.py
