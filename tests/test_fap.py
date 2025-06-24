"""
Financial Analysis Pipeline (FAP) Tests
Tests for the FAP system endpoints and functionality
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_fap_analyze_valid():
    """Test valid FAP analysis request"""
    payload = {
        "name": "Test User",
        "age": 35,
        "income": 100000,
        "risk_tolerance": "moderate",
        "investment_goal": "balanced_growth",
        "investment_horizon": "medium-term"
    }
    resp = client.post("/api/v1/fap/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "fap_context" in data
    assert "history" in data["fap_context"]
    assert len(data["fap_context"]["history"]) > 0
    assert data["used_fallback"] is False

def test_fap_analyze_fallback():
    """Test FAP analysis with fallback to coordinator agent"""
    payload = {
        "name": "Test User",
        "age": 35,
        "income": 100000,
        "risk_tolerance": "moderate",
        "investment_goal": "balanced_growth",
        "investment_horizon": "medium-term",
        "fallback": True
    }
    resp = client.post("/api/v1/fap/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["used_fallback"] is True
    assert data["fallback_response"] is not None

def test_fap_analyze_invalid():
    """Test FAP analysis with invalid request data"""
    payload = {
        # Missing required fields
        "name": "Test User"
    }
    resp = client.post("/api/v1/fap/analyze", json=payload)
    assert resp.status_code == 422  # Unprocessable Entity 