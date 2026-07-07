from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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
    