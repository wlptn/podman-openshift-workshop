# From Your Laptop to a Cluster

A hands-on lab: build and run a small containerized app with **Podman**, group it
into a **pod**, then deploy the very same app to **OpenShift** and scale it.

> **The app** — a tiny Flask web page that counts hits, backed by **Redis**. The
> web tier is *stateless* (it stores nothing itself); Redis holds the count. That
> split is the whole point: it's why the web tier can scale, and why it needs a
> backing service alongside it.

---

## What is a pod?

A **pod** is the smallest deployable unit in Kubernetes and OpenShift: **one or
more containers that are always scheduled together, share a network, and can
share storage.** Containers in the same pod reach each other over `localhost`,
as if they were processes on one small machine.

You rarely run a bare container in production — you run pods. Podman uses the
exact same concept on your laptop, which is why everything here transfers
directly to OpenShift.

---

## Part 1 · Podman — build, run, and pod it locally

### 1. Build an image
```bash
podman build -t sandbox-app .
```
An **image** is your app plus its dependencies, frozen into one portable
artifact. The recipe is the `Dockerfile`.

### 2. Run a single container
```bash
podman run -d -p 8080:5000 --name web sandbox-app
```
Open **http://localhost:8080** — the page loads, but shows **"Waiting for Redis..."**
instead of a hit counter. That's the point: the web tier runs fine on its own, but
one container is only half the app — the counter needs its Redis companion.
```bash
podman rm -f web
```

### 3. Run the whole app with Compose
```bash
podman compose up -d
podman ps            # two containers: web and redis
curl localhost:8000  # the page renders; refresh and the counter climbs
```
Compose runs the two containers side by side on a shared network. The web
container finds Redis by the name `redis` (set via `REDIS_HOST` in
`docker-compose.yml`).
```bash
podman compose down
```

### 4. Run it as a pod

Remove the single container from Step 2 first, so it isn't holding port 8080:
```bash
podman rm -f web
```

Now create a **pod** from `pod.yaml`. This one command provisions **both**
containers together — the web app *and* Redis — inside a single pod that shares
one network:
```bash
podman kube play pod.yaml
podman pod ps        # one pod: hitcounter, with both containers inside
```

Open **http://localhost:8080** — the counter works immediately, because
containers in a pod share the network (Redis is on `localhost`, set by
`REDIS_HOST` in `pod.yaml`). A pod is the exact unit OpenShift schedules, and
`pod.yaml` is Kubernetes YAML — so you've just written your first manifest.
```bash
podman kube down pod.yaml   # stop the pod when you're done
```

---

## Part 2 · The transition — reaching a real cluster

You built that image **on your laptop**. The OpenShift lab is a **separate
environment** that can't see it. In the real world you'd push the image to a
shared registry via a CI/CD pipeline. For this lab we let **OpenShift build the
image itself from the source** — a convenient shortcut for learning.

---

## Part 3 · OpenShift — deploy the same app and scale it

### 1. Log in
```bash
oc login ...        # from the console: top-right menu -> Copy login command
oc whoami
```

### 2. Deploy Redis first
```bash
oc new-app redis:alpine --name=redis
```
Creates a Redis Deployment **and a Service named `redis`** — the name our app
looks for.

### 3. Build & deploy the web app from source
```bash
oc new-app <your-repo-url> --strategy=docker
oc logs -f bc/web   # watch the in-cluster build
```
OpenShift clones the repo, builds the image in the cluster, and rolls it out. The
web pod finds Redis by the `redis` Service name — the same `REDIS_HOST` default
that worked in Compose.

### 4. See it running as pods
```bash
oc get pods
```

### 5. Give it a public URL
```bash
oc create route edge web --service=web --insecure-policy=Redirect
oc get route web
```

### 6. Scale up and down
```bash
oc scale deployment/web --replicas=3
oc get pods -w
```
Refresh the app — the counter keeps climbing correctly across all three web
pods, because they share the one Redis. Then scale back:
```bash
oc scale deployment/web --replicas=1
```

> **Pod vs. Service, made concrete:** locally, web and Redis shared one pod and
> talked over `localhost`. On OpenShift they're *separate* Deployments talking
> through the `redis` Service — which is exactly what lets you scale the web tier
> on its own.

---

## Takeaways
- **Same image, anywhere** — build once, run on a laptop or a cluster.
- **Pods are the unit** — one or more containers scheduled together; identical in Podman and OpenShift.
- **Stateless + backing service** — a stateless web tier plus a shared Redis is what makes scaling safe.
- **Declarative platform** — you state the desired count; OpenShift keeps it true.

## Cheat sheet
| Podman (local) | OpenShift (cluster) |
|---|---|
| `podman build -t sandbox-app .` | `oc new-app <repo> --strategy=docker` |
| `podman compose up -d` | `oc get pods` |
| `podman kube play pod.yaml` | `oc create route edge web --service=web` |
| `podman pod ps` | `oc scale deployment/web --replicas=3` |
| `podman kube down pod.yaml` | `oc delete all -l app=web` |
