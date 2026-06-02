"""
Unit tests for the High School Activities API endpoints.

Tests are structured using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the API call being tested
- Assert: Verify the response and side effects
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange: No setup needed, activities are loaded by fixture

        # Act: Fetch all activities
        response = client.get("/activities")

        # Assert: Verify response
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all expected activities are present
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Soccer Team" in activities
        assert "Swimming Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Team" in activities
        assert "Robotics Club" in activities

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has all required fields."""
        # Arrange: No setup needed

        # Act: Fetch all activities
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify structure of each activity
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_shows_current_participants(self, client):
        """Test that activities return their current participants."""
        # Arrange: No setup needed, fixtures have predefined participants

        # Act: Fetch activities
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify specific participant data
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_succeeds_with_valid_email(self, client):
        """Test successful signup for an activity."""
        # Arrange: Prepare valid activity and email
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act: Sign up for the activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Verify successful signup
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Arrange: Prepare valid activity and email
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participants = client.get("/activities").json()[activity_name]["participants"]

        # Act: Sign up for the activity
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Verify participant was added
        updated_participants = client.get("/activities").json()[activity_name]["participants"]
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_fails_for_already_registered_student(self, client):
        """Test that signup fails when student is already registered."""
        # Arrange: Prepare email that's already registered
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act: Attempt to sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_fails_for_nonexistent_activity(self, client):
        """Test that signup fails when activity doesn't exist."""
        # Arrange: Prepare non-existent activity
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_students_for_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity."""
        # Arrange: Prepare activity and multiple emails
        activity_name = "Chess Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act: Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email1}"
        )
        # Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )

        # Assert: Both signups succeed and both are in participants
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 4  # Original 2 + 2 new


class TestRemoveParticipantFromActivity:
    """Tests for POST /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_succeeds(self, client):
        """Test successful removal of a participant."""
        # Arrange: Prepare activity and participant to remove
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Remove participant
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )

        # Assert: Verify successful removal
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_remove_participant_updates_activity(self, client):
        """Test that remove actually removes the participant from the activity."""
        # Arrange: Prepare activity and participant to remove
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act: Remove participant
        client.post(f"/activities/{activity_name}/remove?email={email}")

        # Assert: Verify participant was removed
        updated_participants = client.get("/activities").json()[activity_name]["participants"]
        assert email not in updated_participants
        assert len(updated_participants) == initial_count - 1

    def test_remove_fails_for_nonparticipant(self, client):
        """Test that remove fails when student is not in the activity."""
        # Arrange: Prepare email not in the activity
        activity_name = "Chess Club"
        email = "nonmember@mergington.edu"

        # Act: Attempt to remove
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )

        # Assert: Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_remove_fails_for_nonexistent_activity(self, client):
        """Test that remove fails when activity doesn't exist."""
        # Arrange: Prepare non-existent activity
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to remove
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )

        # Assert: Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_remove_multiple_participants_independently(self, client):
        """Test that removing one participant doesn't affect others."""
        # Arrange: Prepare participants to remove
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"

        # Act: Remove one participant
        client.post(
            f"/activities/{activity_name}/remove?email={email_to_remove}"
        )

        # Assert: Verify only the specified participant was removed
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert email_to_remove not in participants
        assert email_to_keep in participants


class TestSignupAndRemoveWorkflow:
    """Integration-style tests verifying signup and remove work together."""

    def test_signup_then_remove_participant(self, client):
        """Test that a participant can signup and then be removed."""
        # Arrange: Prepare activity and email
        activity_name = "Chess Club"
        email = "workflow@mergington.edu"

        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Signup succeeds
        assert signup_response.status_code == 200
        participants_after_signup = client.get("/activities").json()[activity_name]["participants"]
        assert email in participants_after_signup

        # Act: Remove the participant
        remove_response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )

        # Assert: Remove succeeds
        assert remove_response.status_code == 200
        participants_after_remove = client.get("/activities").json()[activity_name]["participants"]
        assert email not in participants_after_remove

    def test_cannot_signup_twice_for_same_activity(self, client):
        """Test that a participant cannot signup for the same activity twice."""
        # Arrange: Prepare activity and email
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"

        # Act: First signup
        first_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: First signup succeeds
        assert first_signup.status_code == 200

        # Act: Second signup attempt
        second_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Second signup fails
        assert second_signup.status_code == 400
        assert "already signed up" in second_signup.json()["detail"].lower()
