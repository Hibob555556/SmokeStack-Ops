from fastapi.testclient import TestClient
import pytest

from app import main

app = main.app
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_incident_state():
    """
    Describe: Test setup
    It Should: Keep incident state deterministic between tests.
    """

    main.incident_active_until = 0
    main.incident_source = None
    main.next_random_incident_at = main.time.time() + 3600
    yield


def test_health_endpoint_returns_healthy():
    """
    Describe: Health endpoint
    It Should: Return a 200 status code and a JSON response indicating the service is healthy.
    """

    # Arrange: Define the expected response values
    expected_status_code = 200
    expected_status = "healthy"
    expected_service = "smokestack-ops"

    # Act: Send a GET request to the /health endpoint
    response = client.get("/health")

    # Assert: Verify that the response status code and JSON content match the expected values
    assert response.status_code == expected_status_code
    assert response.json()["status"] == expected_status
    assert response.json()["service"] == expected_service


def test_ready_endpoint_returns_ready():
    """
    Describe: Ready endpoint
    It Should: Return a 200 status code and a JSON response indicating the service is ready.
    """

    # Arrange: Define the expected response values
    expected_status_code = 200
    expected_status = "ready"

    # Act: Send a GET request to the /ready endpoint
    response = client.get("/ready")

    # Assert: Verify that the response status code and JSON content match the expected values
    assert response.status_code == expected_status_code
    assert response.json()["status"] == expected_status


def test_grills_endpoint_returns_grills():
    """
    Describe: Grills endpoint
    It Should: Return a 200 status code and a JSON response containing the list of grills.
    """

    # Arrange: Define the expected response values and JSON keys
    expected_status_code = 200
    min_expected_grills_length = 1
    grills_key = "grills"
    current_temp_key = "current_temp"

    # Act: Send a GET request to the /grills endpoint
    response = client.get("/grills")
    data = response.json()

    # Assert: Verify that the endpoint returns a successful response
    assert response.status_code == expected_status_code

    # Assert: Verify that the response contains grill telemetry data
    assert grills_key in data
    assert len(data[grills_key]) >= min_expected_grills_length
    assert current_temp_key in data[grills_key][0]


def test_metrics_endpoint_returns_prometheus_metrics():
    """
    Describe: Metrics endpoint
    It Should: Return a 200 status code and a response containing Prometheus metrics.
    """

    # Arrange: Define the expected response values and metric names
    expected_status_code = 200
    request_counter_metric = "smokestack_api_requests_total"
    active_grills_metric = "smokestack_active_grills"

    # Act: Send a GET request to the /metrics endpoint
    response = client.get("/metrics")

    # Assert: Verify that the metrics endpoint returns successfully
    assert response.status_code == expected_status_code

    # Assert: Verify that project-specific Prometheus metrics are exposed
    assert request_counter_metric in response.text
    assert active_grills_metric in response.text


def test_simulate_spike_sets_critical_prometheus_metric():
    """
    Describe: Temperature spike simulation
    It Should: Set a deterministic critical temperature metric for alert testing.
    """

    # Arrange: Define the expected spike values
    expected_status_code = 200
    expected_grill_id = "grill-incident-demo"
    expected_temperature = 625

    # Act: Trigger a spike and then scrape metrics
    spike_response = client.post("/simulate/spike")
    metrics_response = client.get("/metrics")

    # Assert: Verify the spike response is critical and alertable
    assert spike_response.status_code == expected_status_code
    assert spike_response.json()["grill_id"] == expected_grill_id
    assert spike_response.json()["current_temp"] == expected_temperature
    assert spike_response.json()["severity"] == "critical"
    assert spike_response.json()["duration_seconds"] == 60
    assert spike_response.json()["expires_at"] > int(main.time.time())

    # Assert: Verify Prometheus can scrape the alerting time series
    expected_metric = (
        f'smokestack_grill_temperature_fahrenheit{{grill_id="{expected_grill_id}"}} '
        f"{float(expected_temperature)}"
    )
    assert expected_metric in metrics_response.text


def test_expired_spike_returns_to_safe_prometheus_metric():
    """
    Describe: Temperature spike expiration
    It Should: Drop the incident metric below the alert threshold after one minute.
    """

    # Arrange: Start an incident that has already expired
    main.start_temperature_incident(source="manual", now=main.time.time() - 61)

    # Act: Scrape metrics after the incident window
    response = client.get("/metrics")

    # Assert: Verify the incident series is no longer alerting
    expected_metric = (
        f'smokestack_grill_temperature_fahrenheit{{grill_id="{main.INCIDENT_GRILL_ID}"}} '
        f"{float(main.INCIDENT_IDLE_TEMP)}"
    )
    assert expected_metric in response.text


def test_random_schedule_starts_temporary_incident():
    """
    Describe: Random incident schedule
    It Should: Start a temporary incident when the scheduled time is reached.
    """

    # Arrange: Force the random schedule to be due
    current_time = main.time.time()
    main.next_random_incident_at = current_time - 1

    # Act: Update the incident scheduler
    is_active = main.update_temperature_incident(now=current_time)

    # Assert: Verify a scheduled incident started for one minute
    assert is_active is True
    assert main.incident_source == "scheduled"
    assert int(main.incident_active_until) == int(current_time + main.INCIDENT_DURATION_SECONDS)


def test_health_endpoint_includes_request_id_header():
    """
    Describe: Health endpoint
    It Should: Include a request ID in the response headers.
    """

    # Arrange: Define the expected response values
    expected_status_code = 200
    request_id_header = "X-Request-ID"

    # Act: Send a GET request to the /health endpoint
    response = client.get("/health")

    # Assert: Verify that the endpoint returns successfully
    assert response.status_code == expected_status_code

    # Assert: Verify that the response includes a non-empty request ID for log correlation
    assert request_id_header in response.headers
    assert len(response.headers[request_id_header]) > 0
    
