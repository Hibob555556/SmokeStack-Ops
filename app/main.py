from fastapi import FastAPI
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import random
import time

app = FastAPI(
    title="SmokeStack Ops",
    description="A DevOps portfolio service that simulates smart grill telemetry.",
    version="0.1.0",
)

REQUEST_COUNT = Counter(
    "smokestack_api_requests_total",
    "Total API requests received by SmokeStack Ops",
    ["endpoint"],
)

ACTIVE_GRILLS = Gauge(
    "smokestack_active_grills",
    "Number of active grills reporting telemetry",
)

GRILL_TEMP = Gauge(
    "smokestack_grill_temperature_fahrenheit",
    "Current grill temperature in Fahrenheit",
    ["grill_id"],
)

PELLET_LEVEL = Gauge(
    "smokestack_pellet_level_percent",
    "Current pellet level percentage",
    ["grill_id"],
)


def generate_grill_data():
    grills = []

    for grill_id in range(1, 6):
        current_temp = random.randint(180, 450)
        pellet_level = random.randint(10, 100)

        grill = {
            "grill_id": f"grill-{grill_id}",
            "target_temp": 225,
            "current_temp": current_temp,
            "pellet_level": pellet_level,
            "firmware_version": "1.0.3",
            "status": "online" if pellet_level > 15 else "low_pellets",
            "last_seen": int(time.time()),
        }

        grills.append(grill)

        GRILL_TEMP.labels(grill_id=grill["grill_id"]).set(current_temp)
        PELLET_LEVEL.labels(grill_id=grill["grill_id"]).set(pellet_level)

    ACTIVE_GRILLS.set(len(grills))

    return grills


@app.get("/health")
def health():
    REQUEST_COUNT.labels(endpoint="/health").inc()

    return {
        "status": "healthy",
        "service": "smokestack-ops",
    }


@app.get("/ready")
def ready():
    REQUEST_COUNT.labels(endpoint="/ready").inc()

    return {
        "status": "ready",
        "dependencies": {
            "database": "not_required_for_mvp",
            "message_queue": "not_required_for_mvp",
        },
    }


@app.get("/grills")
def get_grills():
    REQUEST_COUNT.labels(endpoint="/grills").inc()

    return {
        "grills": generate_grill_data(),
    }


@app.post("/simulate/spike")
def simulate_temperature_spike():
    REQUEST_COUNT.labels(endpoint="/simulate/spike").inc()

    grill_id = "grill-incident-demo"
    spike_temp = random.randint(500, 650)

    GRILL_TEMP.labels(grill_id=grill_id).set(spike_temp)

    return {
        "event": "temperature_spike",
        "grill_id": grill_id,
        "current_temp": spike_temp,
        "severity": "warning" if spike_temp < 600 else "critical",
    }


@app.get("/metrics")
def metrics():
    REQUEST_COUNT.labels(endpoint="/metrics").inc()

    generate_grill_data()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )