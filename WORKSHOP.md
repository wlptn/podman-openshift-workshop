# From Laptop to Cluster: Containers with Podman & OpenShift

A 20-minute hands-on exercise. Students build and run a small web app locally
with **Podman**, then deploy the *same* app to **OpenShift** and scale it.

> The app: a Flask "hello / page-hit counter" web page backed by Redis.
> The web tier is stateless; Redis holds the counter. That split is the whole
> point — it's why we can scale the web tier and why it needs a backing service.

---

## Before you start

Two SEPARATE lab environments (they cannot see each other's files or images):

- **Lab A — Podman:** a Podman Desktop machine, terminal open, this repo cloned.
- **Lab B — OpenShift:** a terminal already logged in (`oc whoami` works), plus
  the OpenShift web console open. Each student has their own project/namespace.

Total time budget: ~10 min in Lab A, ~1 min transition, ~9 min in Lab B.

---

## Part 1 · Lab A — Build and run it locally with Podman  (~10 min)

**Goal:** turn source code into an *image*, run it as a *container*, then run
the full app (web + redis) with one command.

### 1. Build an image
```bash
podman build -t sandbox-app .
```
*An image is your app + its dependencies + how to start it, frozen into one
portable artifact. The recipe is the `Dockerfile`.*

```bash
podman images        # see the image you just made
```

### 2. Run a container from that image
```bash
podman run -d -p 8080:5000 --name web sandbox-app
podman ps            # your image is now a running container
```
*A container is a running instance of an image. `-d` runs it in the background;
`-p 8080:5000` maps your laptop's port 8080 to the app's port 5000.*

Peek at the logs:
```bash
podman logs web
```
*You'll see it complaining it can't reach Redis — this app is TWO pieces, and a
single container is only one of them. That's our cue for `compose`.*

```bash
podman rm -f web     # clear it before the full-stack run
```

### 3. Run the whole app with Compose
```bash
podman compose up -d
```
*`docker-compose.yml` describes BOTH services (web + redis) and wires them
together on one network. One command brings up the complete app.*

```bash
podman ps                    # two containers now: web and redis
curl localhost:8000          # the page renders; refresh and the counter climbs
```
Open **http://localhost:8000** in the browser and refresh a few times.

### 4. Tear it down
```bash
podman compose down
```

✅ **You built an image, ran a container, and ran a multi-service app locally.**

---

## Part 2 · The transition — how does this reach a real cluster?  (~1 min, TALK)

You just built an image **on this laptop**. The OpenShift lab is a **completely
separate environment** — it cannot see that image.

In the real world you bridge that gap by putting the image somewhere both sides
can reach: **push it to a shared registry** (Quay, an internal registry, …),
usually from a **CI/CD pipeline** that builds it once and promotes it.

For this workshop we'll use a convenient shortcut: **OpenShift builds the image
itself, from the app's source code.** Great for learning — but call it out as a
shortcut. In production you'd build once in a pipeline and ship a versioned
image, not rebuild inside every cluster.

> Same app, new home. Watch it become *pods*.

---

## Part 3 · Lab B — Deploy the same app to OpenShift  (~9 min)

**Goal:** get the app running as pods, expose it, and scale it.

### 1. Confirm where you are
```bash
oc whoami
oc project            # your personal namespace
```

### 2. Deploy Redis first (the backing service)
```bash
oc new-app redis:alpine --name=redis
```
*OpenShift pulls the public Redis image and creates a Deployment + Service.
Redis first, so the `redis` service name exists the moment web starts up.*

### 3. Let OpenShift build & deploy the web app from source
```bash
oc new-app https://github.com/redhat-developer-demos/podman-desktop-sandbox-learning-path \
  --name=web --strategy=docker
```
*OpenShift clones the repo, builds the image **in the cluster** from the
Dockerfile, stores it in the internal registry, and rolls out a Deployment +
Service — no laptop image needed.*

Watch the build (optional):
```bash
oc logs -f bc/web        # Ctrl-C once it says "Push successful"
```

### 4. See your app running as a pod  ⭐
```bash
oc get pods
```
*`web-...` Running and `redis-...` Running. This is the moment: your app is a
pod on a real cluster.*

### 5. Give it a public URL
```bash
oc create route edge web --service=web --insecure-policy=Redirect
oc get route web
```
*A Route is the public front door. `edge` adds HTTPS at the router;
`--insecure-policy=Redirect` sends http → https. Open the URL in a browser.*

> Tip: if a route ever shows **"Application is not available"**, it's the
> Route/Service layer, not your code — usually http-vs-https or a port mismatch.

### 6. Scale up and down  ⭐
```bash
oc scale deployment/web --replicas=3
oc get pods -w           # watch three web pods appear; Ctrl-C to stop
```
Refresh the app a few times — the counter keeps climbing correctly even across
3 pods, *because they all share the one Redis.* That's the stateless-web idea.

```bash
oc scale deployment/web --replicas=1
```
*You declare the desired count; OpenShift makes reality match. That's the whole
mindset — describe what you want, the platform maintains it.*

✅ **You deployed the same app to OpenShift, exposed it, and scaled it.**

---

## Why this matters (the takeaway)

- **Same image, anywhere.** Build once, run on a laptop or a cluster — no "works
  on my machine."
- **Small, independent pieces.** A stateless web tier + a shared backing service
  is what lets you scale safely.
- **Declarative platform.** You state the desired end state; OpenShift keeps it
  true (restarts, scaling, rollouts).

## Try it yourself at home
- **Podman Desktop** — https://podman-desktop.io  (build & run locally, free)
- **OpenShift Developer Sandbox** — https://developers.redhat.com/developer-sandbox
  (a free hosted cluster; `oc login`, then the Part 3 commands work as-is)
- **OpenShift Local (CRC)** — run a single-node OpenShift on your own machine

## Command cheat-sheet
| Podman (local)             | OpenShift (cluster)                          |
|----------------------------|----------------------------------------------|
| `podman build -t app .`    | `oc new-app <git-url> --strategy=docker`     |
| `podman run -d -p .. app`  | `oc get pods`                                |
| `podman compose up -d`     | `oc create route edge web --service=web`     |
| `podman ps` / `podman logs`| `oc scale deployment/web --replicas=3`       |
| `podman compose down`      | `oc delete all -l app=web`                   |

*The declarative equivalent of the OpenShift commands lives in `k8s/`.*
