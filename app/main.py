import json
import logging
import random
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smokestack")

INCIDENT_GRILL_ID = "grill-incident-demo"
CRITICAL_SPIKE_TEMP = 625
INCIDENT_IDLE_TEMP = 225
INCIDENT_DURATION_SECONDS = 60
RANDOM_INCIDENT_MIN_DELAY_SECONDS = 180
RANDOM_INCIDENT_MAX_DELAY_SECONDS = 420

incident_active_until = 0
incident_source = None
next_random_incident_at = time.time() + random.randint(
    RANDOM_INCIDENT_MIN_DELAY_SECONDS,
    RANDOM_INCIDENT_MAX_DELAY_SECONDS,
)

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


def schedule_next_random_incident(now=None):
    """
    Description: Schedules the next random demo incident.
    Returns:
        int: Unix timestamp when the next random incident should start.
    """
    global next_random_incident_at

    current_time = now if now is not None else time.time()
    next_random_incident_at = current_time + random.randint(
        RANDOM_INCIDENT_MIN_DELAY_SECONDS,
        RANDOM_INCIDENT_MAX_DELAY_SECONDS,
    )

    return int(next_random_incident_at)


def start_temperature_incident(source, now=None):
    """
    Description: Starts a temporary critical temperature incident.
    Returns:
        int: Unix timestamp when the incident expires.
    """
    global incident_active_until, incident_source

    current_time = now if now is not None else time.time()
    incident_active_until = current_time + INCIDENT_DURATION_SECONDS
    incident_source = source
    GRILL_TEMP.labels(grill_id=INCIDENT_GRILL_ID).set(CRITICAL_SPIKE_TEMP)

    return int(incident_active_until)


def update_temperature_incident(now=None):
    """
    Description: Updates the incident metric and starts random scheduled incidents.
    Returns:
        bool: True when an incident is currently active.
    """
    global incident_active_until, incident_source

    current_time = now if now is not None else time.time()

    if incident_active_until > current_time:
        GRILL_TEMP.labels(grill_id=INCIDENT_GRILL_ID).set(CRITICAL_SPIKE_TEMP)
        return True

    if incident_source is not None:
        incident_active_until = 0
        incident_source = None
        schedule_next_random_incident(current_time)

    if current_time >= next_random_incident_at:
        start_temperature_incident(source="scheduled", now=current_time)
        return True

    GRILL_TEMP.labels(grill_id=INCIDENT_GRILL_ID).set(INCIDENT_IDLE_TEMP)
    return False


@app.middleware("http")
async def log_request_called(request: Request, call_next):
    """
    Description: Middleware to log API requests and responses.
    Parameters:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler to call.
    Returns:
        Response: The HTTP response returned by the next middleware or route handler.
    Throws:
        Exception: If an error occurs during request processing, it will be logged and re-raised.
    """

    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Store the request method and path for logging
    method = request.method
    path = request.url.path
    
    # Store the start time and status code for later
    start_time = time.perf_counter()
    status_code = 500 # initialize to 500 in case of an unhandled exception

    # Attempt to process the request 
    try:
        # Asynchronously call the next middleware or route handler
        response = await call_next(request)
        
        # Pull the status code from the response for logging
        status_code = response.status_code
        
    except Exception:
        # Store the duration of the request in milliseconds for logging
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Log the exception with relevant request information
        logger.exception(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "event": "request_failed",
                }
            )
        )

        # Re-raise the exception to propagate it up the call stack
        raise

    # Calculate request duration and attach the request ID to the response for log correlation
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    # Log the request completion with relevant information
    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
                "event": "request_completed",
            }
        )
    )

    # Return the response to the client
    return response


def generate_grill_data():
    """
    Description: Generates simulated telemetry data for a set of smart grills.
    
    Returns:
        list: A list of dictionaries containing telemetry data for each grill.
    """
    
    grills = []

    # Generate telemetry data for 5 grills
    for grill_id in range(1, 6):
        # Simulate current temperature and pellet level for each grill
        current_temp = random.randint(180, 450)
        pellet_level = random.randint(10, 100)

        # Create a dictionary representing the telemetry data for the grill
        grill = {
            "grill_id": f"grill-{grill_id}",
            "target_temp": 225,
            "current_temp": current_temp,
            "pellet_level": pellet_level,
            "firmware_version": "1.0.3",
            "status": "online" if pellet_level > 15 else "low_pellets",
            "last_seen": int(time.time()),
        }
        
        # Store the generated grill telemetry data in the list of grills
        grills.append(grill)

        # Set the Prometheus metrics for the current temperature and pellet level of the grill
        GRILL_TEMP.labels(grill_id=grill["grill_id"]).set(current_temp)
        PELLET_LEVEL.labels(grill_id=grill["grill_id"]).set(pellet_level)

    # Set the number of active grills in Prometheus metrics
    ACTIVE_GRILLS.set(len(grills))
    update_temperature_incident()

    return grills


@app.get("/health")
def health():
    """
    Description: Checks the health of the service.
    Returns:
        dict: A dictionary containing the health status of the service.
    """
    REQUEST_COUNT.labels(endpoint="/health").inc()

    return {
        "status": "healthy",
        "service": "smokestack-ops",
    }


@app.get("/ready")
def ready():
    """
    Description: Checks if the service is ready to handle requests. this differs 
                 from health in that it checks for dependencies and other factors 
                 that may affect readiness.
    Returns:
        dict: A dictionary containing the readiness status of the service.
    """
    
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
    """
    Description: Retrieves telemetry data for all smart grills.
    Returns:
        dict: A dictionary containing the telemetry data for all grills.
    """
    
    REQUEST_COUNT.labels(endpoint="/grills").inc()

    return {
        "grills": generate_grill_data(),
    }


@app.post("/simulate/spike")
def simulate_temperature_spike():
    """
    Description: Simulates a temperature spike event for a smart grill.
    Returns:
        dict: A dictionary containing the details of the simulated temperature spike event.
    """
    
    REQUEST_COUNT.labels(endpoint="/simulate/spike").inc()

    expires_at = start_temperature_incident(source="manual")

    return {
        "event": "temperature_spike",
        "grill_id": INCIDENT_GRILL_ID,
        "current_temp": CRITICAL_SPIKE_TEMP,
        "severity": "critical",
        "alert_threshold": 600,
        "duration_seconds": INCIDENT_DURATION_SECONDS,
        "expires_at": expires_at,
    }


@app.get("/metrics")
def metrics():
    """
    Description: Exposes Prometheus metrics for monitoring.
    Returns:
        Response: A Prometheus metrics response containing the current metrics data.
    """
    REQUEST_COUNT.labels(endpoint="/metrics").inc()

    generate_grill_data()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
