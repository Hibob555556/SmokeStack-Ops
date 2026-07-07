# High Temperature Incident Runbook

## Purpose

This runbook supports the `HighGrillTemperature` Prometheus alert for SmokeStack Ops.

The alert fires when:

```promql
smokestack_grill_temperature_fahrenheit > 600
```

for 30 seconds.

## Expected Demo Behavior

The demo incident grill is:

```text
grill-incident-demo
```

Manual incidents are started with:

```powershell
curl.exe -X POST http://localhost:8000/simulate/spike
```

The API reports `625F` for 60 seconds, then returns the incident grill to `225F`.

Prometheus scrapes each API pod through the headless `smokestack-api-metrics` Service. Because the incident state is held in API pod memory, the alert labels include the pod target that reported the spike through the `instance` label.

The API can also start random scheduled one-minute demo incidents during `/metrics` scrapes. Each API pod schedules these independently every 3-7 minutes.

## Verify The Alert

Open Prometheus:

```text
http://localhost:9090
```

Check the alert:

```promql
ALERTS{alertname="HighGrillTemperature"}
```

Check the incident metric:

```promql
smokestack_grill_temperature_fahrenheit{grill_id="grill-incident-demo"}
```

Expected active incident value:

```text
625
```

Expected resolved value:

```text
225
```

## Kubernetes Checks

Verify Prometheus is scraping API pods:

```powershell
kubectl get endpoints smokestack-api-metrics -n smokestack
kubectl logs deployment/prometheus -n smokestack
```

Verify API pods are healthy:

```powershell
kubectl get pods -n smokestack -l app=smokestack-api
kubectl logs -n smokestack -l app=smokestack-api --tail=100
```

## Resolution

For demo incidents, wait for the 60-second incident window to expire. The alert should clear after Prometheus scrapes the safe `225F` value and evaluates the rule again.

If the alert does not clear:

```powershell
kubectl rollout restart deployment smokestack-api -n smokestack
kubectl rollout status deployment smokestack-api -n smokestack
```

Then confirm the metric has returned below threshold:

```promql
smokestack_grill_temperature_fahrenheit{grill_id="grill-incident-demo"}
```
