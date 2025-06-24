"""
Tests for the user profile service
"""

import pytest
from pathlib import Path
import json
import shutil
from datetime import datetime

from src.services.user_profile_service import UserProfileService
from src.models.user_profile import UserProfile, InvestmentPreference

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

def test_create_default_profile(user_profile_service):
    """Test creating a default user profile"""
    profile = user_profile_service.create_default_profile(
        user_id="test123",
        name="Test User",
        age=30,
        income=100000
    )
    
    assert profile.user_id == "test123"
    assert profile.name == "Test User"
    assert profile.age == 30
    assert profile.income == 100000
    assert profile.risk_tolerance == "moderate"
    assert profile.investment_goal == "balanced_growth"
    assert profile.investment_horizon == "long-term"
    assert len(profile.preferences) == 3
    
    # Verify file was created
    assert user_profile_service.profile_file.exists()

def test_save_and_load_profile(user_profile_service):
    """Test saving and loading a user profile"""
    # Create a test profile
    preferences = [
        InvestmentPreference(
            asset_type="stocks",
            allocation_percentage=60,
            risk_tolerance="moderate"
        ),
        InvestmentPreference(
            asset_type="bonds",
            allocation_percentage=40,
            risk_tolerance="conservative"
        )
    ]
    
    profile = UserProfile(
        user_id="test123",
        name="Test User",
        age=30,
        income=100000,
        risk_tolerance="moderate",
        investment_goal="balanced_growth",
        investment_horizon="long-term",
        preferences=preferences
    )
    
    # Save profile
    assert user_profile_service.save_profile(profile)
    
    # Load profile
    loaded_profile = user_profile_service.load_profile()
    assert loaded_profile is not None
    assert loaded_profile.user_id == profile.user_id
    assert loaded_profile.name == profile.name
    assert loaded_profile.age == profile.age
    assert loaded_profile.income == profile.income
    assert len(loaded_profile.preferences) == len(profile.preferences)

def test_update_preferences(user_profile_service):
    """Test updating user preferences"""
    # Create initial profile
    profile = user_profile_service.create_default_profile(
        user_id="test123",
        name="Test User",
        age=30,
        income=100000
    )
    
    # Update preferences
    new_preferences = [
        InvestmentPreference(
            asset_type="stocks",
            allocation_percentage=70,
            risk_tolerance="aggressive"
        ),
        InvestmentPreference(
            asset_type="bonds",
            allocation_percentage=30,
            risk_tolerance="conservative"
        )
    ]
    
    assert user_profile_service.update_preferences(new_preferences)
    
    # Verify changes
    updated_profile = user_profile_service.load_profile()
    assert updated_profile is not None
    assert len(updated_profile.preferences) == 2
    assert updated_profile.preferences[0].allocation_percentage == 70
    assert updated_profile.preferences[1].allocation_percentage == 30

def test_get_portfolio_summary(user_profile_service):
    """Test getting portfolio summary"""
    # Create a profile
    user_profile_service.create_default_profile(
        user_id="test123",
        name="Test User",
        age=30,
        income=100000
    )
    
    # Get summary
    summary = user_profile_service.get_portfolio_summary()
    
    assert "error" not in summary
    assert summary["user_id"] == "test123"
    assert summary["name"] == "Test User"
    assert summary["risk_tolerance"] == "moderate"
    assert summary["investment_goal"] == "balanced_growth"
    assert summary["investment_horizon"] == "long-term"
    assert "total_allocation" in summary
    assert "asset_allocation" in summary
    assert "last_updated" in summary

def test_get_portfolio_summary_no_profile(user_profile_service):
    """Test getting portfolio summary when no profile exists"""
    summary = user_profile_service.get_portfolio_summary()
    assert "error" in summary
    assert summary["error"] == "No user profile found" 