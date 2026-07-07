New-Item -ItemType Directory -Force -Path docs | Out-Null

@'
# SmokeStack Ops Kubernetes Runbook

## Purpose

This runbook documents how to deploy, verify, troubleshoot, and clean up the SmokeStack Ops API in a local Kubernetes environment.

SmokeStack Ops runs as a containerized FastAPI service with:

- Kubernetes Namespace
- ConfigMap
- Deployment
- Two API replicas
- ClusterIP Service
- Liveness probe
- Readiness probe
- CPU and memory requests/limits

---

## Prerequisites

Before deploying, confirm that Kubernetes is running:

```powershell
kubectl config current-context
kubectl cluster-info
```

Expected local context used during testing:

```text
rancher-desktop
```

If `kubectl cluster-info` cannot connect to `127.0.0.1:6443`, the local Kubernetes cluster is not running.

---

## Build the Docker Image

From the project root:

```powershell
docker build -f docker/Dockerfile -t smokestack:latest .
```

This builds the local image used by the Kubernetes Deployment.

---

## Deploy to Kubernetes

Apply the namespace first:

```powershell
kubectl apply -f k8s/namespace.yaml
```

Then apply the remaining manifests:

```powershell
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Or apply the full folder after the namespace exists:

```powershell
kubectl apply -f k8s/
```

---

## Verify the Deployment

Check all Kubernetes resources in the `smokestack` namespace:

```powershell
kubectl get all -n smokestack
```

Expected result:

```text
pod/smokestack-api-...   1/1   Running
pod/smokestack-api-...   1/1   Running

service/smokestack-api-service   ClusterIP   ...   80/TCP

deployment.apps/smokestack-api   2/2   2   2
```

---

## Test the Service Locally

Port-forward the Kubernetes Service:

```powershell
kubectl port-forward service/smokestack-api-service 8000:80 -n smokestack
```

In a second terminal, test the API:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
curl.exe http://localhost:8000/grills
curl.exe http://localhost:8000/metrics
```

Expected `/health` response:

```json
{"status":"healthy","service":"smokestack-ops"}
```

Expected `/ready` response:

```json
{"status":"ready","dependencies":{"database":"not_required_for_mvp","message_queue":"not_required_for_mvp"}}
```

---

## Troubleshooting

### Check Pod Status

```powershell
kubectl get pods -n smokestack
```

Healthy pods should show:

```text
READY   STATUS    RESTARTS
1/1     Running   0
```

---

### Describe the Deployment

Use this when replicas are not becoming available:

```powershell
kubectl describe deployment smokestack-api -n smokestack
```

Look for:

- Failed scheduling
- Image pull errors
- Probe failures
- Resource issues

---

### Describe Pods

```powershell
kubectl describe pod -l app=smokestack-api -n smokestack
```

Use this to inspect:

- Events
- Container state
- Liveness probe failures
- Readiness probe failures
- Image pull problems

---

### View Application Logs

```powershell
kubectl logs -l app=smokestack-api -n smokestack
```

The app emits structured JSON logs with:

- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`
- `client_ip`
- `event`

Example log:

```json
{"request_id":"...","method":"GET","path":"/health","status_code":200,"duration_ms":2.14,"client_ip":"127.0.0.1","event":"request_completed"}
```

---

## Common Issue: Kubernetes Cannot Connect

Error:

```text
Unable to connect to the server: dial tcp 127.0.0.1:6443
```

Cause:

The local Kubernetes cluster is not running.

Fix:

Start Kubernetes in Rancher Desktop or Docker Desktop, then verify:

```powershell
kubectl cluster-info
```

---

## Common Issue: Namespace Not Found

Error:

```text
namespaces "smokestack" not found
```

Cause:

Kubernetes tried to create namespace-scoped resources before the namespace was ready.

Fix:

Apply the namespace first:

```powershell
kubectl apply -f k8s/namespace.yaml
```

Then apply the other manifests:

```powershell
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## Common Issue: Service Missing

Check services:

```powershell
kubectl get svc -n smokestack
```

If the service is missing:

```powershell
kubectl apply -f k8s/service.yaml
```

---

## Common Issue: Image Pull Failure

Check pod status:

```powershell
kubectl get pods -n smokestack
```

If you see:

```text
ImagePullBackOff
```

Rebuild the image locally:

```powershell
docker build -f docker/Dockerfile -t smokestack:latest .
```

Then restart the deployment:

```powershell
kubectl rollout restart deployment smokestack-api -n smokestack
```

---

## Restart the Deployment

```powershell
kubectl rollout restart deployment smokestack-api -n smokestack
```

Check rollout status:

```powershell
kubectl rollout status deployment smokestack-api -n smokestack
```

---

## Scale the Deployment

Scale to one replica:

```powershell
kubectl scale deployment smokestack-api --replicas=1 -n smokestack
```

Scale back to two replicas:

```powershell
kubectl scale deployment smokestack-api --replicas=2 -n smokestack
```

---

## Clean Up

Delete all SmokeStack Kubernetes resources:

```powershell
kubectl delete -f k8s/
```

If needed, delete the namespace directly:

```powershell
kubectl delete namespace smokestack
```

---

## Operational Notes

The `/health` endpoint is used by the liveness probe to determine whether the container should be restarted.

The `/ready` endpoint is used by the readiness probe to determine whether the pod is ready to receive traffic.

The `/metrics` endpoint exposes Prometheus-compatible metrics for future observability work.

The `X-Request-ID` response header supports request tracing and log correlation during troubleshooting.
'@ | Set-Content -Encoding UTF8 docs/kubernetes-runbook.md