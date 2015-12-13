import base64
import pathlib
import re
import shutil
import subprocess
import tempfile
import threading

import bottle
import datadog
from first import first

SECONDS_IN_YEAR = 365 * 24 * 3600

# initialize datadog
datadog.initialize()
stats = datadog.ThreadStats()
stats.start()

lock = threading.Semaphore(4)


def metric_name(suffix):
    return "pr0gramm.thumby.%s" % suffix


def make_thumbnail(url):
    path = pathlib.Path(tempfile.mkdtemp(suffix="thumby"))
    try:
        command = ["timeout", "-s", "KILL", "10s",
                   "ffmpeg", "-y", "-i", url, "-vf", "scale='if(gt(iw,1024),1024,iw)':-1",
                   "-f", "image2", "-t", "3", "-r", "1", "-q:v", "20", "out-%04d.webp"]

        subprocess.check_call(command, cwd=str(path))

        thumb = first(sorted(path.glob("out-*.webp"), reverse=True))
        if not thumb:
            raise IOError("could not generate thumbnail")

        return thumb.open("rb")

    finally:
        shutil.rmtree(str(path), ignore_errors=True)


@bottle.route("/:url")
@stats.timed(metric_name("request"))
def thumbnail_route(url):
    url = base64.urlsafe_b64decode(url.encode("ascii")).strip().decode("utf8")
    if not re.match("^https?://[^/]*pr0gramm.com/.*$", url):
        return bottle.abort(403)

    # use only http
    url = url.replace("https://", "http://")

    try:
        with lock:
            image_fp = make_thumbnail(url)
    except:
        stats.increment(metric_name("error"))
        raise

    bottle.response.add_header("Content-Type", "image/webp")
    bottle.response.add_header("Cache-Control", "max-age={}".format(SECONDS_IN_YEAR))
    return image_fp
