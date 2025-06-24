"""
Tests for the API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil

from src.api.main import app
from src.services.user_profile_service import UserProfileService

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def user_profile_service():
    """Create a UserProfileService instance for testing"""
    service = UserProfileService()
    # Use a test data directory
    service.data_dir = Path("test_data")
    service.profile_file = service.data_dir / "user_profile.json"
    yield service
    # Cleanup after tests
    if service.data_dir.exists():
        shutil.rmtree(service.data_dir)

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_profile(client, user_profile_service):
    """Test creating a user profile"""
    profile_data = {
        "name": "Test User",
        "age": 30,
        "income": 100000,
        "risk_tolerance": "moderate",
        "investment_goal": "balanced_growth",
        "investment_horizon": "long-term"
    }
    
    response = client.post("/api/v1/profile", json=profile_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "user_id" in data
    assert data["name"] == profile_data["name"]
    assert data["risk_tolerance"] == profile_data["risk_tolerance"]
    assert data["investment_goal"] == profile_data["investment_goal"]
    assert data["investment_horizon"] == profile_data["investment_horizon"]
    assert "preferences" in data

def test_get_portfolio_summary_no_profile(client):
    """Test getting portfolio summary when no profile exists"""
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 404
    assert "error" in response.json()

def test_get_portfolio_summary_with_profile(client, user_profile_service):
    """Test getting portfolio summary with an existing profile"""
    # Create a profile first
    profile_data = {
        "name": "Test User",
        "age": 30,
        "income": 100000,
        "risk_tolerance": "moderate",
        "investment_goal": "balanced_growth",
        "investment_horizon": "long-term"
    }
    
    client.post("/api/v1/profile", json=profile_data)
    
    # Get portfolio summary
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "user_id" in data
    assert data["name"] == profile_data["name"]
    assert "total_allocation" in data
    assert "asset_allocation" in data
    assert "last_updated" in data

def test_chat_endpoint(client):
    """Test the chat endpoint"""
    message = "What's a good investment strategy for retirement?"
    response = client.post("/api/v1/chat", json={"message": message})
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_with_user_id(client, user_profile_service):
    """Test the chat endpoint with a user ID"""
    # Create a profile first
    profile_data = {
        "name": "Test User",
        "age": 30,
        "income": 100000,
        "risk_tolerance": "moderate",
        "investment_goal": "balanced_growth",
        "investment_horizon": "long-term"
    }
    
    profile_response = client.post("/api/v1/profile", json=profile_data)
    user_id = profile_response.json()["user_id"]
    
    # Test chat with user ID
    message = "What's a good investment strategy for retirement?"
    response = client.post("/api/v1/chat", json={"message": message, "user_id": user_id})
    assert response.status_code == 200
    assert "response" in response.json() 