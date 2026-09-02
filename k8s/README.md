# k8s/ — the declarative ("GitOps") way to deploy on OpenShift

These manifests describe the SAME app the workshop deploys with `oc new-app`.
The live 20-minute exercise uses the `oc new-app` commands (fewer steps, and
OpenShift builds the image for you). These files are the "here's what those
commands created, written down" reference — useful for the concepts portion
and for anyone who wants to see the real Kubernetes objects.

Objects: redis Deployment + Service, web Deployment + Service, web Route.

## Using them
Order matters — redis first so its Service name resolves when web starts:

    oc apply -f k8s/redis-deployment.yaml -f k8s/redis-service.yaml
    oc apply -f k8s/web-deployment.yaml  -f k8s/web-service.yaml -f k8s/web-route.yaml

## One thing you MUST edit first
`web-deployment.yaml` needs an image the cluster can pull. Because the Podman
lab and the OpenShift lab are separate environments, the image you built
locally does NOT exist here. Two real-world options:
  1. Let OpenShift build it once:  `oc new-app <git-url> --strategy=docker`
     then point the manifest at the resulting ImageStream:
       image-registry.openshift-image-registry.svc:5000/<YOUR-NAMESPACE>/web:latest
  2. Push the image to a shared registry (Quay, etc.) both environments reach,
     and use that reference.
Replace `REPLACE-NAMESPACE` in web-deployment.yaml accordingly.

This "how does the image get from my laptop to the cluster?" question is the
key idea of the workshop — see WORKSHOP.md, the transition section.
