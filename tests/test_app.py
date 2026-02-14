"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original activities
    original_activities = {
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and demonstrations",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art creation",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["maya@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theatrical production, and performance opportunities",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Tennis Team": {
            "description": "Tennis coaching, practice matches and competitive tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["noah@mergington.edu"]
        },
        "Swimming Team": {
            "description": "Competitive swimming training and meet preparation",
            "schedule": "Tuesday, Wednesday, Friday, 4:30 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training, drills and inter-school games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["riley@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer practice, fitness and weekend matches",
            "schedule": "Tuesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["harper@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test (not strictly necessary but good practice)
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Debate Club" in data
        assert "Science Club" in data
        assert "Chess Club" in data
        assert len(data) == 11
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Debate Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_includes_existing_participants(self, client):
        """Test that activities show current participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Debate Club"]["participants"]
        assert "james@mergington.edu" in data["Drama Club"]["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client):
        """Test successful signup adds participant to activity"""
        response = client.post(
            "/activities/Debate%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Debate Club"]["participants"]
        assert "newstudent@mergington.edu" in participants
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Test signup with email already registered returns 400"""
        response = client.post(
            "/activities/Debate%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_full_activity_returns_400(self, client):
        """Test signup to full activity returns 400"""
        # First, get a small activity and fill it
        activities["Chess Club"]["max_participants"] = 2
        activities["Chess Club"]["participants"] = ["user1@mergington.edu", "user2@mergington.edu"]
        
        response = client.post(
            "/activities/Chess%20Club/signup?email=newuser@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successfully_removes_participant(self, client):
        """Test successful unregister removes participant from activity"""
        # Add a participant first
        client.post(
            "/activities/Debate%20Club/signup?email=tempstudent@mergington.edu"
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Debate%20Club/unregister?email=tempstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Debate Club"]["participants"]
        assert "tempstudent@mergington.edu" not in participants
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_non_participant_returns_400(self, client):
        """Test unregister non-registered participant returns 400"""
        response = client.delete(
            "/activities/Debate%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_existing_participant_succeeds(self, client):
        """Test unregister removes existing participant successfully"""
        response = client.delete(
            "/activities/Debate%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Debate Club"]["participants"]
        assert "alex@mergington.edu" not in participants


class TestActivityConstraints:
    """Tests for activity constraints and edge cases"""
    
    def test_signup_updates_availability(self, client):
        """Test that signup correctly updates spot availability"""
        initial_response = client.get("/activities")
        initial_activity = initial_response.json()["Debate Club"]
        initial_spots = initial_activity["max_participants"] - len(initial_activity["participants"])
        
        # Sign up a new participant
        client.post(
            "/activities/Debate%20Club/signup?email=newstudent@mergington.edu"
        )
        
        # Check availability decreased
        updated_response = client.get("/activities")
        updated_activity = updated_response.json()["Debate Club"]
        updated_spots = updated_activity["max_participants"] - len(updated_activity["participants"])
        
        assert updated_spots == initial_spots - 1
    
    def test_unregister_updates_availability(self, client):
        """Test that unregister correctly updates spot availability"""
        # Add a participant
        client.post(
            "/activities/Debate%20Club/signup?email=tempstudent@mergington.edu"
        )
        
        filled_response = client.get("/activities")
        filled_activity = filled_response.json()["Debate Club"]
        filled_spots = filled_activity["max_participants"] - len(filled_activity["participants"])
        
        # Unregister the participant
        client.delete(
            "/activities/Debate%20Club/unregister?email=tempstudent@mergington.edu"
        )
        
        # Check availability increased
        cleared_response = client.get("/activities")
        cleared_activity = cleared_response.json()["Debate Club"]
        cleared_spots = cleared_activity["max_participants"] - len(cleared_activity["participants"])
        
        assert cleared_spots == filled_spots + 1
