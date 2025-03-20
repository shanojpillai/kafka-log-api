import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test that the health endpoint returns the expected response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    
def test_dataset_info():
    """Test that the dataset info endpoint returns data."""
    response = client.get("/api/v1/dataset/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_logs" in data
    assert "sample" in data
    
def test_send_log():
    """Test sending a log entry."""
    log_data = {
        "service": "test-service",
        "level": "ERROR",
        "message": "Test error message",
        "metadata": {
            "test_id": "test-001"
        }
    }
    response = client.post("/api/v1/log", json=log_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify the log was stored
    logs_response = client.get("/api/v1/logs?service=test-service")
    assert logs_response.status_code == 200
    logs_data = logs_response.json()
    assert logs_data["count"] > 0
    
    # Check that our log is in the results
    log_found = False
    for log in logs_data["logs"]:
        if (log["service"] == "test-service" and 
            log["level"] == "ERROR" and 
            log["message"] == "Test error message"):
            log_found = True
            break
    assert log_found, "Sent log was not found in logs endpoint response"