from __future__ import division
from __future__ import unicode_literals

import shutil
import tempfile
import subprocess
import threading
import base64
import re

import pathlib
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, send_file
from first import first


def make_thumbnail(url, target):
    path = pathlib.Path(tempfile.mkdtemp(suffix="thumby"))
    try:
        command = ["avconv", "-i", url, "-r", "1", "-f", "image2", "-t", "3", "out-%d.jpg"]
        subprocess.check_call(command, cwd=str(path))

        image = first(sorted(path.glob("out-*.jpg"), reverse=True))
        if not image:
            raise IOError("could not generate thumbnail")

        shutil.copy(str(image), str(target))

    finally:
        shutil.rmtree(str(path), ignore_errors=True)


class Thumby(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.pool = ThreadPoolExecutor(4)
        self.jobs = {}

        self.images = pathlib.Path("images/")
        if not self.images.exists():
            self.images.mkdir()

    def thumbnail(self, url):
        with self.lock:
            try:
                return self.jobs[url]
            except KeyError:
                future = self.pool.submit(self._thumbnail, url)
                self.jobs[url] = future
                return future

    def _thumbnail(self, url):
        target = self.images / re.sub("[^a-z0-9]", "_", url.lower())
        if not target.exists() or not target.stat().st_size:
            make_thumbnail(url, target)

        return target


def make_app():
    thumby = Thumby()

    app = Flask(__name__)

    @app.route("/<url>/thumb.jpg")
    def thumbnail_route(url):
        url = base64.urlsafe_b64decode(url.encode("ascii")).strip()
        image = thumby.thumbnail(url).result()
        return send_file(str(image), mimetype="image/jpeg")

    return app


if __name__ == "__main__":
    make_app().run(host="0.0.0.0", threaded=True)
