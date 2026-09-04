import os
import redis
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# The Redis hostname comes from an environment variable so the same image
# works everywhere: "redis" by default (the service name used by Compose
# and OpenShift), overridable with REDIS_HOST. A short connect timeout keeps
# the page fast when Redis isn't there yet.
cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=6379,
    socket_connect_timeout=1,
)


def get_hit_count():
    # Increment the counter in Redis. If Redis isn't reachable yet, return
    # None so the page still renders — the counter just won't show until
    # Redis is up. Refresh once it is, and the count starts working.
    try:
        return cache.incr("hits")
    except redis.exceptions.RedisError:
        return None


@app.route("/")
@app.route("/<count>")
def hello(count=None):
    count = get_hit_count()
    return render_template("index.html", count=count)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
