# SmokeStack Ops

SmokeStack Ops is a DevOps portfolio project that simulates telemetry from a fleet of smart pellet grills.

The application is intentionally small so the main focus stays on DevOps practices: Docker, CI/CD, Kubernetes, infrastructure as code, observability, structured logging, vulnerability scanning, and operational documentation.

## Project Purpose

SmokeStack Ops was built to demonstrate hands-on DevOps fundamentals for a Junior DevOps Engineer role.

The project shows how a small API can be packaged, tested, deployed, monitored, and documented using production-style engineering practices.

## Current Features

* Python FastAPI service
* Simulated smart grill telemetry
* Health and readiness endpoints
* Prometheus-compatible metrics endpoint
* Structured JSON request logging
* Request correlation with `X-Request-ID`
* Docker containerization
* Docker Compose local runtime
* GitHub Actions CI pipeline
* Python linting with flake8
* Automated tests with pytest
* Docker image build validation in CI
* Container startup verification in CI
* Trivy vulnerability scanning in CI
* Local Kubernetes deployment manifests
* Kubernetes Namespace, ConfigMap, Deployment, and Service
* Kubernetes liveness and readiness probes
* CPU and memory requests/limits
* Prometheus monitoring in Kubernetes
* Grafana dashboard provisioning in Kubernetes
* Validate-only Terraform AWS infrastructure blueprint
* Operational runbooks and troubleshooting documentation

## Tech Stack

| Area | Technology |
| --- | --- |
| API | Python, FastAPI |
| Testing | pytest |
| Linting | flake8 |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Security Scanning | Trivy |
| Orchestration | Kubernetes |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Infrastructure as Code | Terraform |
| Cloud Blueprint | AWS ECR, IAM, CloudWatch |

## Application Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Liveness-style service health check |
| `GET /ready` | Readiness-style dependency check |
| `GET /grills` | Returns simulated smart grill telemetry |
| `POST /simulate/spike` | Simulates a grill temperature spike |
| `GET /metrics` | Exposes Prometheus-compatible metrics |

## Example API Responses

### `GET /health`

    {
      "status": "healthy",
      "service": "smokestack-ops"
    }

### `GET /ready`

    {
      "status": "ready",
      "dependencies": {
        "database": "not_required_for_mvp",
        "message_queue": "not_required_for_mvp"
      }
    }

### `GET /grills`

    {
      "grills": [
        {
          "grill_id": "grill-1",
          "target_temp": 225,
          "current_temp": 349,
          "pellet_level": 90,
          "firmware_version": "1.0.3",
          "status": "online",
          "last_seen": 1783438264
        }
      ]
    }

## Prometheus Metrics

SmokeStack Ops exposes custom metrics from the `/metrics` endpoint.

| Metric | Type | Purpose |
| --- | --- | --- |
| `smokestack_api_requests_total` | Counter | Tracks API requests by endpoint |
| `smokestack_active_grills` | Gauge | Tracks active simulated grills |
| `smokestack_grill_temperature_fahrenheit` | Gauge | Tracks grill temperature by grill ID |
| `smokestack_pellet_level_percent` | Gauge | Tracks pellet level by grill ID |

Example metric:

    smokestack_grill_temperature_fahrenheit{grill_id="grill-1"} 349.0

The spike endpoint sets a deterministic critical demo reading for 60 seconds:

    smokestack_grill_temperature_fahrenheit{grill_id="grill-incident-demo"} 625.0

After the one-minute incident window, the demo incident grill returns to a safe idle temperature. Prometheus scrapes can also start random scheduled one-minute demo incidents every 3-7 minutes per API pod.

## Structured Logging

Each request is logged as structured JSON.

Example log:

    {
      "request_id": "d95fa691-98e5-4796-a64f-f26482401f94",
      "method": "GET",
      "path": "/health",
      "status_code": 200,
      "duration_ms": 2.14,
      "client_ip": "127.0.0.1",
      "event": "request_completed"
    }

Each response includes an `X-Request-ID` header for request tracing and log correlation.

Example:

    x-request-id: d95fa691-98e5-4796-a64f-f26482401f94

## Repository Structure

    SmokeStack/
    ├─ .github/
    │  └─ workflows/
    │     └─ ci.yml
    ├─ app/
    │  ├─ __init__.py
    │  ├─ main.py
    │  └─ tests/
    │     └─ test_health.py
    ├─ docker/
    │  └─ Dockerfile
    ├─ docs/
    │  ├─ images/
    │  │  └─ grafana-dashboard.png
    │  ├─ kubernetes-runbook.md
    │  └─ observability.md
    ├─ k8s/
    │  ├─ namespace.yaml
    │  ├─ configmap.yaml
    │  ├─ deployment.yaml
    │  └─ service.yaml
    ├─ monitoring/
    │  ├─ prometheus-config.yaml
    │  ├─ prometheus-deployment.yaml
    │  ├─ prometheus-service.yaml
    │  ├─ grafana-datasource.yaml
    │  ├─ grafana-dashboard-provider.yaml
    │  ├─ grafana-dashboard-smokestack.yaml
    │  ├─ grafana-deployment.yaml
    │  └─ grafana-service.yaml
    ├─ terraform/
    │  └─ aws/
    │     ├─ providers.tf
    │     ├─ variables.tf
    │     ├─ main.tf
    │     ├─ outputs.tf
    │     └─ README.md
    ├─ .dockerignore
    ├─ .gitignore
    ├─ docker-compose.yml
    ├─ pytest.ini
    ├─ requirements.txt
    └─ README.md

## Prerequisites

For local development:

* Python 3.12+
* Docker
* Docker Compose
* Kubernetes environment such as Rancher Desktop, Docker Desktop Kubernetes, minikube, or kind
* kubectl
* Git

Terraform is not required locally for this project because Terraform validation runs in GitHub Actions.

## Run Locally with Python

From the project root:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    pytest
    uvicorn app.main:app --reload

Open:

    http://localhost:8000/health
    http://localhost:8000/ready
    http://localhost:8000/grills
    http://localhost:8000/metrics

## Run Locally with Docker Compose

From the project root:

    docker compose up --build

Test the API:

    curl.exe http://localhost:8000/health
    curl.exe http://localhost:8000/ready
    curl.exe http://localhost:8000/grills
    curl.exe http://localhost:8000/metrics

## Run Tests

From the project root:

    pytest

Expected result:

    app/tests/test_health.py .....

## Docker Image

Build the Docker image manually:

    docker build -f docker/Dockerfile -t smokestack:latest .

Run the container manually:

    docker run -d --name smokestack-api -p 8000:8000 smokestack:latest

Test the running container:

    curl.exe http://localhost:8000/health

Stop and remove the container:

    docker stop smokestack-api
    docker rm smokestack-api

## CI/CD Pipeline

SmokeStack Ops uses GitHub Actions for continuous integration.

The CI workflow:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs dependencies
4. Runs flake8 syntax and quality checks
5. Runs pytest
6. Builds the Docker image
7. Scans the image with Trivy
8. Starts the container
9. Verifies the `/health` endpoint
10. Prints container logs on failure
11. Cleans up the container after the run

This validates both the application and the container runtime behavior on every push or pull request to `main`.

## Kubernetes Deployment

SmokeStack Ops can be deployed to a local Kubernetes cluster.

### Build the local image

    docker build -f docker/Dockerfile -t smokestack:latest .

### Apply Kubernetes manifests

Apply the namespace first:

    kubectl apply -f k8s/namespace.yaml

Apply the remaining manifests:

    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/metrics-service.yaml

### Verify Kubernetes resources

    kubectl get all -n smokestack

Expected resources include:

    pod/smokestack-api-...
    pod/smokestack-api-...
    service/smokestack-api-service
    service/smokestack-api-metrics
    deployment.apps/smokestack-api
    replicaset.apps/smokestack-api-...

### Port-forward the API service

    kubectl port-forward service/smokestack-api-service 8000:80 -n smokestack

In another terminal:

    curl.exe http://localhost:8000/health
    curl.exe http://localhost:8000/ready
    curl.exe http://localhost:8000/grills
    curl.exe http://localhost:8000/metrics

## Kubernetes Configuration

The Kubernetes deployment includes:

* `Namespace` for resource isolation
* `ConfigMap` for environment configuration
* `Deployment` with two replicas
* `Service` for internal cluster routing
* Headless metrics `Service` for per-pod Prometheus discovery
* Liveness probe using `/health`
* Readiness probe using `/ready`
* CPU and memory requests
* CPU and memory limits

## Prometheus Monitoring

Prometheus is deployed in the `smokestack` namespace and scrapes each API pod through the headless metrics Service DNS name:

    smokestack-api-metrics.smokestack.svc.cluster.local:8000

Apply Prometheus manifests:

    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/metrics-service.yaml
    kubectl apply -f monitoring/prometheus-config.yaml
    kubectl apply -f k8s/prometheus/alert-rules.yaml
    kubectl apply -f monitoring/prometheus-deployment.yaml
    kubectl apply -f monitoring/prometheus-service.yaml

Port-forward Prometheus:

    kubectl port-forward service/prometheus-service 9090:9090 -n smokestack

Open:

    http://localhost:9090

Useful Prometheus queries:

    smokestack_api_requests_total
    smokestack_active_grills
    smokestack_grill_temperature_fahrenheit
    smokestack_pellet_level_percent

Trigger a demo alertable spike:

    curl.exe -X POST http://localhost:8000/simulate/spike

The `HighGrillTemperature` alert fires when Prometheus scrapes `smokestack_grill_temperature_fahrenheit > 600` for 30 seconds. The manual spike remains active for 60 seconds, then drops back below the alert threshold. The API also schedules random one-minute demo incidents every 3-7 minutes per API pod during Prometheus scrapes.

## Grafana Dashboard

Grafana is deployed in Kubernetes and provisioned with:

* Prometheus data source
* Dashboard provider
* SmokeStack Ops dashboard

Apply Grafana manifests:

    kubectl apply -f monitoring/grafana-datasource.yaml
    kubectl apply -f monitoring/grafana-dashboard-provider.yaml
    kubectl apply -f monitoring/grafana-dashboard-smokestack.yaml
    kubectl apply -f monitoring/grafana-deployment.yaml
    kubectl apply -f monitoring/grafana-service.yaml

Port-forward Grafana:

    kubectl port-forward service/grafana-service 3000:3000 -n smokestack

Open:

    http://localhost:3000

Default local credentials:

    Username: admin
    Password: admin

Dashboard path:

    Dashboards → SmokeStack → SmokeStack Ops

## Dashboard Screenshot



The dashboard visualizes:

* Active grills
* API requests by endpoint
* Grill temperatures
* Pellet levels

## Terraform AWS Blueprint

This project includes a validate-only Terraform AWS blueprint.

The Terraform files define:

* AWS ECR repository for container images
* CloudWatch log group for future application logs
* IAM policy for GitHub Actions image publishing

This project intentionally does not run:

    terraform apply

The goal is to demonstrate Infrastructure as Code practices without provisioning paid cloud resources.

Terraform validation runs in GitHub Actions using:

    terraform fmt -check
    terraform init -backend=false
    terraform validate

This keeps the project cost-conscious while still showing AWS and Terraform awareness.

## Documentation

Additional documentation is available in the `docs/` folder.

| Document | Purpose |
| --- | --- |
| `docs/kubernetes-runbook.md` | Kubernetes deployment and troubleshooting runbook |
| `docs/observability.md` | Prometheus, Grafana, metrics, and logging guide |
| `terraform/aws/README.md` | Terraform AWS blueprint explanation |

## Troubleshooting

### Kubernetes cannot connect

Error:

    Unable to connect to the server: dial tcp 127.0.0.1:6443

Cause:

The local Kubernetes cluster is not running.

Fix:

Start Kubernetes in Rancher Desktop, Docker Desktop, minikube, or kind, then run:

    kubectl cluster-info

### Namespace not found

Error:

    namespaces "smokestack" not found

Fix:

Apply the namespace first:

    kubectl apply -f k8s/namespace.yaml

Then apply the remaining manifests.

### Image pull failure

Error:

    ImagePullBackOff

Fix:

Rebuild the local image:

    docker build -f docker/Dockerfile -t smokestack:latest .

Restart the deployment:

    kubectl rollout restart deployment smokestack-api -n smokestack

### View application logs

    kubectl logs -l app=smokestack-api -n smokestack

### View Grafana logs

    kubectl logs deployment/grafana -n smokestack

### View Prometheus logs

    kubectl logs deployment/prometheus -n smokestack

## Cleanup

Delete monitoring resources:

    kubectl delete -f monitoring/

Delete application Kubernetes resources:

    kubectl delete -f k8s/

Delete both:

    kubectl delete -f monitoring/
    kubectl delete -f k8s/

## Portfolio Summary

SmokeStack Ops demonstrates practical DevOps skills through a small but production-style application environment.

The project includes:

* API development with health and readiness checks
* Containerized runtime with Docker
* CI validation with GitHub Actions
* Automated test execution
* Docker image build verification
* Security scanning with Trivy
* Kubernetes deployment with probes and resource controls
* Prometheus metrics collection
* Grafana dashboard visualization
* Structured JSON logs
* Request ID correlation
* Validate-only Terraform AWS infrastructure blueprint
* Operational documentation and troubleshooting runbooks

## Resume Bullet

Built SmokeStack Ops, a DevOps portfolio project simulating smart grill telemetry using Python, FastAPI, Docker, GitHub Actions, Kubernetes, Prometheus, Grafana, Trivy, and Terraform. Implemented CI validation, container health checks, vulnerability scanning, Kubernetes probes, custom metrics, structured logs, dashboard provisioning, and validate-only AWS infrastructure as code.

## Interview Pitch

SmokeStack Ops is a DevOps-focused project where the application is intentionally simple, but the operational environment is realistic.

I built a FastAPI service that simulates smart grill telemetry, containerized it with Docker, added automated tests, created a GitHub Actions pipeline, scanned the image with Trivy, deployed it locally to Kubernetes, and added Prometheus and Grafana for observability.

I also documented runbooks for deployment, troubleshooting, monitoring, and Kubernetes operations. For AWS, I created a validate-only Terraform blueprint for ECR, IAM, and CloudWatch so I could demonstrate infrastructure as code without creating paid cloud resources.

The project helped me practice the same kinds of tasks a junior DevOps engineer would support: CI/CD, containers, Kubernetes, monitoring, logging, troubleshooting, documentation, and cost-aware cloud planning.
