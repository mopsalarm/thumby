from __future__ import division
from __future__ import unicode_literals

import shutil
import tempfile
import subprocess
import threading
import base64
import re

import datadog
import pathlib
from flask import Flask, send_file
from werkzeug.exceptions import abort


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
        command = ["timeout", "-s", "KILL", "8s",
                   "avconv", "-i", url, "-vf", "scale=640:-1", "-f", "image2", "-t", "4", "out-%04d.jpg"]

        subprocess.check_call(command, cwd=str(path))

        files = sorted(path.glob("out-*.jpg"), reverse=True)
        if not files:
            raise IOError("could not generate thumbnail")

        image = files[len(files) // 2]
        return image.open("rb")

    finally:
        shutil.rmtree(str(path), ignore_errors=True)


def make_app():
    lock = threading.Semaphore(4)

    app = Flask(__name__)

    @app.route("/<url>/thumb.jpg")
    @stats.timed(metric_name("request"))
    def thumbnail_route(url):
        url = base64.urlsafe_b64decode(url.encode("ascii")).strip()
        if not re.match("^https?://[^/]*pr0gramm.com/.*$", url):
            return abort(403)

        # use only http
        url = url.replace("https://", "http://")

        try:
            with lock:
                image_fp = make_thumbnail(url)
        except:
            stats.increment(metric_name("error"))
            raise

        return send_file(image_fp, mimetype="image/jpeg",
                         add_etags=False, cache_timeout=SECONDS_IN_YEAR)

    return app


if __name__ == "__main__":
    make_app().run(host="0.0.0.0", threaded=True)
