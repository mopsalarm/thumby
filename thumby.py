import shutil
import tempfile
import subprocess
import threading
import base64
import re

import datadog
import pathlib
import bottle

from first import first

SECONDS_IN_YEAR = 365 * 24 * 3600

# initialize datadog
datadog.initialize()
stats = datadog.ThreadStats()
stats.start()


def metric_name(suffix):
    return "pr0gramm.thumby.%s" % suffix


def make_thumbnail(url):
    path = pathlib.Path(tempfile.mkdtemp(suffix="thumby"))
    try:
        command = ["timeout", "-s", "KILL", "10s",
                   "ffmpeg", "-i", url, "-vf", "scale=640:-1", "-f", "image2", "-t", "3", "-r", "1", "out-%04d.jpg"]

        subprocess.check_call(command, cwd=str(path))

        thumb = first(sorted(path.glob("out-*.jpg"), reverse=True))
        if not thumb:
            raise IOError("could not generate thumbnail")

        return thumb.open("rb")

    finally:
        shutil.rmtree(str(path), ignore_errors=True)


lock = threading.Semaphore(4)

@bottle.route("/:url/thumb.jpg")
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

    bottle.response.add_header("Content-Type", "image/jpeg")
    bottle.response.add_header("Cache-Control", "max-age={}".format(SECONDS_IN_YEAR))
    return image_fp
