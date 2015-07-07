from python:2-onbuild
MAINTAINER Mopsalarm

ADD http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz /tmp/ffmpeg.tar.xz
RUN xz -d /tmp/ffmpeg.tar.xz && tar -xC/usr/bin -f /tmp/ffmpeg.tar --strip-components 1

# images are placed at /usr/src/app/images
CMD python thumby.py

EXPOSE 5000

