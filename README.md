# Podman → OpenShift Workshop App

A tiny Flask web app that counts page hits, backed by Redis. It's the sample
app for the hands-on lab: build and run it locally with Podman, then deploy
the same image to OpenShift.

## What's here
- `app.py` — the Flask app (a page-hit counter)
- `templates/`, `static/` — the web page and its assets
- `requirements.txt` — Python dependencies (Flask, Redis)
- `Dockerfile` — builds the container image
- `docker-compose.yml` — runs the app + Redis together locally
- `k8s/` — optional Kubernetes/OpenShift manifests

## Run it locally

    podman compose up --build

Then open http://localhost:8000 and refresh — the counter climbs.

## How it finds Redis
The app reads the Redis hostname from the `REDIS_HOST` environment variable
(default: `redis`). Compose sets it for you; on OpenShift the `redis` Service
name resolves the same way.
