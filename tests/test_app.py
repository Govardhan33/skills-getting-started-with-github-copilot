"""
Tests for the Mergington High School Activities API
Following the AAA (Arrange-Act-Assert) testing pattern
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the API"""
    return TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns activities dictionary"""
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == expected_status
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities include known entries"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        expected_status = 200
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup fails for non-existent activity"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup is rejected"""
        # Arrange
        activity_name = "Soccer Team"
        email = "duplicate@mergington.edu"
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Act - Second signup with same email
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()
    
    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds participant to activity"""
        # Arrange
        activity_name = "Drama Club"
        email = "newperson@mergington.edu"
        
        # Act - Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Act - Get updated state
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        updated_count = len(updated_participants)
        
        # Assert
        assert signup_response.status_code == 200
        assert updated_count == initial_count + 1
        assert email in updated_participants


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister"""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Art Club"
        email = "unreg@mergington.edu"
        expected_status = 200
        
        # Act - Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister fails for non-existent activity"""
        # Arrange
        activity_name = "Fake Activity"
        email = "test@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister fails if participant not signed up"""
        # Arrange
        activity_name = "Debate Club"
        email = "notmember@mergington.edu"
        expected_status = 400
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == expected_status
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from activity"""
        # Arrange
        activity_name = "Science Club"
        email = "removeme@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Verify they're signed up
        before_response = client.get("/activities")
        before_participants = before_response.json()[activity_name]["participants"]
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Act - Get updated state
        after_response = client.get("/activities")
        after_participants = after_response.json()[activity_name]["participants"]
        
        # Assert
        assert email in before_participants
        assert email not in after_participants


class TestRootEndpoint:
    """Tests for GET /"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to static index"""
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == expected_status
