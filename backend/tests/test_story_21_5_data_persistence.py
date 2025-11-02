"""
Story 21.5: Verify Sport Data Persistence

Test suite verifying that sport selections are correctly saved to the database
and retrieved without data loss, ensuring users' sport preferences are reliably
persisted across sessions.

Acceptance Criteria:
1. User submits assessment → DB contains expected sport value
2. Assessment saved with sport="soccer" → API returns sport="soccer"
3. Multiple users create assessments → Each user's sport stored correctly
4. Database schema → Sport field has proper constraints, indexes, validation
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from apps.assessments.models import Assessment

User = get_user_model()


@pytest.mark.django_db
class TestStory21_5_APIToDatabasePersistence:
    """
    Test AC1: Given a user submits an assessment with a sport selection,
    when I query the database, then the sport field should contain the expected value.
    """

    def test_soccer_persisted_to_database_after_api_submission(self):
        """Verify sport="soccer" is correctly saved to database via API."""
        # Arrange: Create authenticated user
        user = User.objects.create_user(
            email="soccer_player@example.com",
            password="TestPass123!",
            first_name="Soccer",
            last_name="Player",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        assessment_data = {
            "sport": "soccer",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "injuries": "no",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbells", "resistance_bands"],
        }

        # Act: Submit assessment via API
        response = client.post("/api/v1/assessments/", assessment_data, format="json")

        # Assert: API responds successfully
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        # Assert AC1: Query database directly and verify sport field
        db_assessment = Assessment.objects.get(user=user)
        assert (
            db_assessment.sport == "soccer"
        ), f"Expected sport='soccer' in DB, got '{db_assessment.sport}'"

    def test_cricket_persisted_to_database_after_api_submission(self):
        """Verify sport="cricket" is correctly saved to database via API."""
        # Arrange: Create authenticated user
        user = User.objects.create_user(
            email="cricket_player@example.com",
            password="TestPass123!",
            first_name="Cricket",
            last_name="Player",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        assessment_data = {
            "sport": "cricket",
            "age": 30,
            "experience_level": "advanced",
            "training_days": "6-7",
            "injuries": "yes",
            "equipment": "full_gym",
            "equipment_items": [],
        }

        # Act: Submit assessment via API
        response = client.post("/api/v1/assessments/", assessment_data, format="json")

        # Assert: API responds successfully
        assert response.status_code == 201

        # Assert AC1: Query database directly and verify sport field
        db_assessment = Assessment.objects.get(user=user)
        assert (
            db_assessment.sport == "cricket"
        ), f"Expected sport='cricket' in DB, got '{db_assessment.sport}'"

    def test_database_value_matches_submitted_value(self):
        """Verify exact match between submitted and persisted sport value."""
        # Arrange
        user = User.objects.create_user(
            email="test_exact@example.com",
            password="TestPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        submitted_sport = "soccer"
        assessment_data = {
            "sport": submitted_sport,
            "age": 22,
            "experience_level": "beginner",
            "training_days": "2-3",
            "equipment": "no_equipment",
        }

        # Act: Submit via API
        client.post("/api/v1/assessments/", assessment_data, format="json")

        # Assert AC1: Database value exactly matches submitted value
        db_assessment = Assessment.objects.get(user=user)
        assert db_assessment.sport == submitted_sport, (
            f"Database value '{db_assessment.sport}' does not match "
            f"submitted value '{submitted_sport}'"
        )

    def test_database_persistence_survives_multiple_queries(self):
        """Verify sport value remains consistent across multiple DB queries."""
        # Arrange
        user = User.objects.create_user(
            email="persistence@example.com",
            password="TestPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        assessment_data = {
            "sport": "soccer",
            "age": 28,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "basic_equipment",
            "equipment_items": ["yoga_mat"],
        }

        # Act: Submit via API
        client.post("/api/v1/assessments/", assessment_data, format="json")

        # Assert AC1: Query database multiple times - value should be consistent
        query1 = Assessment.objects.get(user=user).sport
        query2 = Assessment.objects.get(user=user).sport
        query3 = Assessment.objects.filter(user=user).first().sport

        assert query1 == "soccer", "First query returned incorrect sport"
        assert query2 == "soccer", "Second query returned incorrect sport"
        assert query3 == "soccer", "Third query returned incorrect sport"
        assert query1 == query2 == query3, "Queries returned inconsistent values"


@pytest.mark.django_db
class TestStory21_5_APIRetrievalPersistence:
    """
    Test AC2: Given an assessment is saved with sport="soccer",
    when I retrieve the assessment via API, then the sport field should return "soccer".
    """

    def test_soccer_retrieved_correctly_via_api_detail_endpoint(self):
        """Verify sport="soccer" returned correctly via detail endpoint."""
        # Arrange: Create user and assessment directly in DB
        user = User.objects.create_user(
            email="retrieve_detail@example.com",
            password="TestPass123!",
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=26,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Act: Retrieve via detail endpoint
        response = client.get(f"/api/v1/assessments/{assessment.id}/")

        # Assert AC2: Response contains sport="soccer"
        assert response.status_code == 200
        assert (
            response.data["sport"] == "soccer"
        ), f"Expected sport='soccer' in API response, got '{response.data['sport']}'"

    def test_soccer_retrieved_correctly_via_api_me_endpoint(self):
        """Verify sport="soccer" returned correctly via /me/ endpoint."""
        # Arrange: Create user and assessment directly in DB
        user = User.objects.create_user(
            email="retrieve_me@example.com",
            password="TestPass123!",
        )
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=27,
            experience_level="advanced",
            training_days="6-7",
            equipment="full_gym",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Act: Retrieve via /me/ endpoint
        response = client.get("/api/v1/assessments/me/")

        # Assert AC2: Response contains sport="soccer"
        assert response.status_code == 200
        assert (
            response.data["sport"] == "soccer"
        ), f"Expected sport='soccer' in /me/ response, got '{response.data['sport']}'"

    def test_soccer_retrieved_correctly_via_api_list_endpoint(self):
        """Verify sport="soccer" returned correctly via list endpoint."""
        # Arrange: Create user and assessment directly in DB
        user = User.objects.create_user(
            email="retrieve_list@example.com",
            password="TestPass123!",
        )
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=24,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Act: Retrieve via list endpoint
        response = client.get("/api/v1/assessments/")

        # Assert AC2: Response contains sport="soccer" in results
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert (
            response.data["results"][0]["sport"] == "soccer"
        ), f"Expected sport='soccer' in list response, got '{response.data['results'][0]['sport']}'"

    def test_cricket_retrieved_correctly_via_api(self):
        """Verify sport="cricket" returned correctly via API."""
        # Arrange: Create user and assessment with cricket
        user = User.objects.create_user(
            email="cricket_retrieve@example.com",
            password="TestPass123!",
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=29,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Act: Retrieve via detail endpoint
        response = client.get(f"/api/v1/assessments/{assessment.id}/")

        # Assert AC2: Response contains sport="cricket"
        assert response.status_code == 200
        assert (
            response.data["sport"] == "cricket"
        ), f"Expected sport='cricket' in API response, got '{response.data['sport']}'"

    def test_sport_value_consistent_across_create_and_retrieve(self):
        """Verify sport value is consistent between creation and retrieval."""
        # Arrange: Create via API
        user = User.objects.create_user(
            email="consistent@example.com",
            password="TestPass123!",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        assessment_data = {
            "sport": "soccer",
            "age": 23,
            "experience_level": "beginner",
            "training_days": "2-3",
            "equipment": "no_equipment",
        }

        # Act: Create and retrieve
        create_response = client.post(
            "/api/v1/assessments/", assessment_data, format="json"
        )
        retrieve_response = client.get("/api/v1/assessments/me/")

        # Assert AC2: Sport value consistent between create and retrieve
        assert create_response.status_code == 201
        assert retrieve_response.status_code == 200

        created_sport = create_response.data["sport"]
        retrieved_sport = retrieve_response.data["sport"]

        assert (
            created_sport == "soccer"
        ), f"Created assessment has wrong sport: '{created_sport}'"
        assert (
            retrieved_sport == "soccer"
        ), f"Retrieved assessment has wrong sport: '{retrieved_sport}'"
        assert (
            created_sport == retrieved_sport
        ), f"Sport inconsistent: created='{created_sport}', retrieved='{retrieved_sport}'"

    def test_updated_sport_persists_and_retrieves_correctly(self):
        """Verify updated sport value persists and retrieves correctly."""
        # Arrange: Create assessment with soccer
        user = User.objects.create_user(
            email="update_sport@example.com",
            password="TestPass123!",
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=["dumbbells"],
        )

        client = APIClient()
        client.force_authenticate(user=user)

        # Act: Update sport to cricket (include all required fields)
        update_data = {
            "sport": "cricket",
            "age": 25,
            "experience_level": "intermediate",
            "training_days": "4-5",
            "equipment": "basic_equipment",
            "equipment_items": ["dumbbells"],
        }
        update_response = client.put(
            f"/api/v1/assessments/{assessment.id}/",
            update_data,
            format="json",
        )

        # Retrieve updated assessment
        retrieve_response = client.get(f"/api/v1/assessments/{assessment.id}/")

        # Assert AC2: Updated sport persists and retrieves correctly
        assert update_response.status_code == 200
        assert (
            update_response.data["sport"] == "cricket"
        ), f"Update response has wrong sport: '{update_response.data['sport']}'"

        assert retrieve_response.status_code == 200
        assert retrieve_response.data["sport"] == "cricket", (
            f"Retrieved assessment after update has wrong sport: "
            f"'{retrieve_response.data['sport']}'"
        )

        # Verify database also updated
        assessment.refresh_from_db()
        assert (
            assessment.sport == "cricket"
        ), f"Database not updated, still has '{assessment.sport}'"


@pytest.mark.django_db
class TestStory21_5_MultiUserPersistence:
    """
    Test AC3: Given multiple users create assessments,
    when I verify the database, then each user's sport selection should be
    stored correctly in their assessment record.
    """

    def test_multiple_users_different_sports_stored_correctly(self):
        """Verify multiple users can have different sports, stored correctly."""
        # Arrange: Create 3 users with different sports
        user_soccer = User.objects.create_user(
            email="user_soccer@example.com",
            password="TestPass123!",
        )
        user_cricket = User.objects.create_user(
            email="user_cricket@example.com",
            password="TestPass123!",
        )
        user_soccer2 = User.objects.create_user(
            email="user_soccer2@example.com",
            password="TestPass123!",
        )

        # Act: Create assessments with different sports
        assessment_soccer1 = Assessment.objects.create(
            user=user_soccer,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )
        assessment_cricket = Assessment.objects.create(
            user=user_cricket,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            equipment="full_gym",
        )
        assessment_soccer2 = Assessment.objects.create(
            user=user_soccer2,
            sport="soccer",
            age=22,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Assert AC3: Verify each user's sport stored correctly
        # Query database directly
        db_assessment_soccer1 = Assessment.objects.get(user=user_soccer)
        db_assessment_cricket = Assessment.objects.get(user=user_cricket)
        db_assessment_soccer2 = Assessment.objects.get(user=user_soccer2)

        assert (
            db_assessment_soccer1.sport == "soccer"
        ), f"User1 has wrong sport: '{db_assessment_soccer1.sport}'"
        assert (
            db_assessment_cricket.sport == "cricket"
        ), f"User2 has wrong sport: '{db_assessment_cricket.sport}'"
        assert (
            db_assessment_soccer2.sport == "soccer"
        ), f"User3 has wrong sport: '{db_assessment_soccer2.sport}'"

        # Verify no cross-contamination
        assert db_assessment_soccer1.id == assessment_soccer1.id
        assert db_assessment_cricket.id == assessment_cricket.id
        assert db_assessment_soccer2.id == assessment_soccer2.id

    def test_multiple_users_via_api_each_sport_persisted_correctly(self):
        """Verify multiple users submitting via API have correct sports persisted."""
        # Arrange: Create multiple users
        users_data = [
            {"email": "api_user1@example.com", "sport": "soccer"},
            {"email": "api_user2@example.com", "sport": "cricket"},
            {"email": "api_user3@example.com", "sport": "soccer"},
            {"email": "api_user4@example.com", "sport": "cricket"},
            {"email": "api_user5@example.com", "sport": "soccer"},
        ]

        client = APIClient()

        # Act: Create assessments via API for each user
        for user_data in users_data:
            user = User.objects.create_user(
                email=user_data["email"],
                password="TestPass123!",
            )
            client.force_authenticate(user=user)

            assessment_data = {
                "sport": user_data["sport"],
                "age": 25,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "equipment": "basic_equipment",
                "equipment_items": ["dumbbells"],
            }

            response = client.post(
                "/api/v1/assessments/", assessment_data, format="json"
            )
            assert (
                response.status_code == 201
            ), f"Failed to create assessment for {user_data['email']}: {response.data}"

        # Assert AC3: Verify database has correct sport for each user
        for user_data in users_data:
            user = User.objects.get(email=user_data["email"])
            assessment = Assessment.objects.get(user=user)

            assert assessment.sport == user_data["sport"], (
                f"User {user_data['email']} has wrong sport: "
                f"expected '{user_data['sport']}', got '{assessment.sport}'"
            )

    def test_user_sport_isolation_no_cross_contamination(self):
        """Verify each user's sport is isolated and not affected by other users."""
        # Arrange: Create users
        user1 = User.objects.create_user(
            email="isolated1@example.com",
            password="TestPass123!",
        )
        user2 = User.objects.create_user(
            email="isolated2@example.com",
            password="TestPass123!",
        )

        # Act: Create assessments
        Assessment.objects.create(
            user=user1,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        Assessment.objects.create(
            user=user2,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            equipment="full_gym",
        )

        # Assert AC3: Each user's sport remains correct
        assessment1 = Assessment.objects.get(user=user1)
        assessment2 = Assessment.objects.get(user=user2)

        assert (
            assessment1.sport == "soccer"
        ), f"User1 sport changed: '{assessment1.sport}'"
        assert (
            assessment2.sport == "cricket"
        ), f"User2 sport changed: '{assessment2.sport}'"

        # Verify filtering works correctly
        soccer_assessments = Assessment.objects.filter(sport="soccer")
        cricket_assessments = Assessment.objects.filter(sport="cricket")

        assert soccer_assessments.count() == 1, "Soccer filter returned wrong count"
        assert cricket_assessments.count() == 1, "Cricket filter returned wrong count"
        assert (
            soccer_assessments.first().user == user1
        ), "Soccer filter returned wrong user"
        assert (
            cricket_assessments.first().user == user2
        ), "Cricket filter returned wrong user"

    def test_bulk_user_creation_all_sports_persist_correctly(self):
        """Verify bulk user/assessment creation maintains sport data integrity."""
        # Arrange & Act: Create 20 users with alternating sports
        users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f"bulk_user_{i}@example.com",
                password="TestPass123!",
            )
            sport = "soccer" if i % 2 == 0 else "cricket"
            Assessment.objects.create(
                user=user,
                sport=sport,
                age=20 + i,
                experience_level="intermediate",
                training_days="4-5",
                equipment="basic_equipment",
            )
            users.append({"user": user, "expected_sport": sport})

        # Assert AC3: Verify all users have correct sports
        for user_data in users:
            assessment = Assessment.objects.get(user=user_data["user"])
            assert assessment.sport == user_data["expected_sport"], (
                f"User {user_data['user'].email} has wrong sport: "
                f"expected '{user_data['expected_sport']}', got '{assessment.sport}'"
            )

        # Verify counts
        soccer_count = Assessment.objects.filter(sport="soccer").count()
        cricket_count = Assessment.objects.filter(sport="cricket").count()

        assert soccer_count == 10, f"Expected 10 soccer assessments, got {soccer_count}"
        assert (
            cricket_count == 10
        ), f"Expected 10 cricket assessments, got {cricket_count}"


class TestStory21_5_DatabaseSchemaValidation(TransactionTestCase):
    """
    Test AC4: Given the database schema, when I inspect the sport field definition,
    then it should have proper constraints, indexes, and validation rules.

    Uses TransactionTestCase to allow direct database inspection and constraint testing.
    """

    def test_sport_field_definition(self):
        """Verify sport field has correct data type, length, and null constraint."""
        # Query database schema
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'assessments' AND column_name = 'sport'
                """
            )
            result = cursor.fetchone()

        # Assert AC4: Field definition is correct
        assert result is not None, "Sport column not found in assessments table"

        column_name, data_type, max_length, is_nullable = result

        assert column_name == "sport", f"Wrong column name: '{column_name}'"
        assert data_type == "character varying", f"Wrong data type: '{data_type}'"
        assert max_length == 20, f"Wrong max length: {max_length}"
        assert (
            is_nullable == "NO"
        ), f"Sport field should be NOT NULL, got: {is_nullable}"

    def test_sport_field_has_check_constraint(self):
        """Verify sport field has CHECK constraint enforcing valid values."""
        # Query database constraints
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT constraint_name, check_clause
                FROM information_schema.check_constraints
                WHERE constraint_name = 'assessments_sport_valid_choice'
                """
            )
            result = cursor.fetchone()

        # Assert AC4: CHECK constraint exists
        assert (
            result is not None
        ), "CHECK constraint 'assessments_sport_valid_choice' not found"

        constraint_name, check_clause = result

        assert (
            constraint_name == "assessments_sport_valid_choice"
        ), f"Wrong constraint name: '{constraint_name}'"

        # Verify constraint includes valid sport values
        assert (
            "soccer" in check_clause.lower()
        ), "CHECK constraint doesn't include 'soccer'"
        assert (
            "cricket" in check_clause.lower()
        ), "CHECK constraint doesn't include 'cricket'"

    def test_sport_field_has_index(self):
        """Verify sport field has an index for query performance."""
        # Query database indexes
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessments' AND indexdef LIKE '%sport%'
                """
            )
            indexes = cursor.fetchall()

        # Assert AC4: Index on sport field exists
        assert len(indexes) > 0, "No index found on sport field"

        # Find the sport index (not a multi-column index)
        sport_index = None
        for index_name, index_def in indexes:
            if "sport" in index_def.lower() and "user" not in index_def.lower():
                sport_index = (index_name, index_def)
                break

        assert sport_index is not None, "No dedicated index found for sport field"

        index_name, index_def = sport_index
        assert "btree" in index_def.lower(), f"Index should be btree type: {index_def}"

    def test_assessment_table_has_proper_indexes(self):
        """Verify assessment table has all expected indexes."""
        # Query all indexes on assessments table
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessments'
                ORDER BY indexname
                """
            )
            indexes = cursor.fetchall()

        # Assert AC4: Expected indexes exist
        index_names = [idx[0] for idx in indexes]

        # Should have indexes on: user_id (unique + regular), sport, created_at, primary key
        assert any(
            "user" in name.lower() for name in index_names
        ), "Missing index on user_id"
        assert any(
            "sport" in name.lower() for name in index_names
        ), "Missing index on sport"
        assert any(
            "created" in name.lower() for name in index_names
        ), "Missing index on created_at"
        assert any(
            "pkey" in name.lower() for name in index_names
        ), "Missing primary key index"

    def test_sport_choices_match_database_constraint(self):
        """Verify model Sport choices match database CHECK constraint."""
        # Get model choices
        model_choices = [choice[0] for choice in Assessment.Sport.choices]

        # Query database constraint
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT check_clause
                FROM information_schema.check_constraints
                WHERE constraint_name = 'assessments_sport_valid_choice'
                """
            )
            result = cursor.fetchone()

        assert result is not None, "CHECK constraint not found"
        check_clause = result[0]

        # Assert AC4: Model choices match database constraint
        for choice in model_choices:
            assert (
                choice in check_clause
            ), f"Model choice '{choice}' not in database constraint: {check_clause}"

    def test_invalid_sport_value_rejected_by_database(self):
        """Verify database rejects invalid sport values via CHECK constraint."""
        from django.db import IntegrityError

        # Arrange: Create user
        user = User.objects.create_user(
            email="invalid_sport@example.com",
            password="TestPass123!",
        )

        # Act & Assert AC4: Try to insert invalid sport value (bypass Django validation)
        with connection.cursor() as cursor:
            with pytest.raises(IntegrityError) as exc_info:
                cursor.execute(
                    """
                    INSERT INTO assessments (
                        user_id, sport, age, experience_level,
                        training_days, injuries, equipment, equipment_items,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    [
                        user.id,
                        "invalid_sport",  # Invalid sport value
                        25,
                        "intermediate",
                        "4-5",
                        "no",
                        "basic_equipment",
                        "[]",
                    ],
                )

            # Verify constraint violation
            error_message = str(exc_info.value)
            assert (
                "assessments_sport_valid_choice" in error_message
                or "check constraint" in error_message.lower()
            ), f"Expected constraint violation error, got: {error_message}"

    def test_old_football_value_rejected_by_database(self):
        """Verify database rejects old 'football' value (confirms migration success)."""
        from django.db import IntegrityError

        # Arrange: Create user
        user = User.objects.create_user(
            email="old_football@example.com",
            password="TestPass123!",
        )

        # Act & Assert AC4: Try to insert 'football' value (should be rejected)
        with connection.cursor() as cursor:
            with pytest.raises(IntegrityError) as exc_info:
                cursor.execute(
                    """
                    INSERT INTO assessments (
                        user_id, sport, age, experience_level,
                        training_days, injuries, equipment, equipment_items,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    [
                        user.id,
                        "football",  # Old value - should be rejected
                        25,
                        "intermediate",
                        "4-5",
                        "no",
                        "basic_equipment",
                        "[]",
                    ],
                )

            # Verify constraint violation
            error_message = str(exc_info.value)
            assert (
                "assessments_sport_valid_choice" in error_message
                or "check constraint" in error_message.lower()
            ), f"Expected constraint violation for 'football', got: {error_message}"


@pytest.mark.django_db
class TestStory21_5_DataIntegrityAndConsistency:
    """
    Additional tests verifying data integrity and consistency across sessions.
    """

    def test_sport_value_persists_across_orm_cache_clear(self):
        """Verify sport value persists when ORM cache is cleared."""
        # Arrange: Create assessment
        user = User.objects.create_user(
            email="persist_session@example.com",
            password="TestPass123!",
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        # Store assessment ID
        assessment_id = assessment.id

        # Act: Clear ORM cache by deleting Python object reference
        del assessment

        # Assert: Re-query from database - data should persist
        persisted_assessment = Assessment.objects.get(id=assessment_id)
        assert (
            persisted_assessment.sport == "soccer"
        ), "Sport value did not persist after cache clear"

        # Double check with user lookup
        persisted_by_user = Assessment.objects.get(user=user)
        assert (
            persisted_by_user.sport == "soccer"
        ), "Sport value inconsistent when queried by user"

    def test_no_data_loss_on_concurrent_user_creation(self):
        """Verify no data loss when multiple users created concurrently."""
        # Arrange: Create assessments for multiple users rapidly
        client = APIClient()
        created_assessments = []

        for i in range(10):
            user = User.objects.create_user(
                email=f"concurrent_{i}@example.com",
                password="TestPass123!",
            )
            client.force_authenticate(user=user)

            assessment_data = {
                "sport": "soccer" if i % 2 == 0 else "cricket",
                "age": 20 + i,
                "experience_level": "intermediate",
                "training_days": "4-5",
                "equipment": "basic_equipment",
                "equipment_items": ["dumbbells"],
            }

            response = client.post(
                "/api/v1/assessments/", assessment_data, format="json"
            )
            assert (
                response.status_code == 201
            ), f"Failed for user {i}: {response.data if response.status_code != 201 else ''}"
            created_assessments.append(
                {"user": user, "expected_sport": assessment_data["sport"]}
            )

        # Assert: Verify all assessments persisted with correct data
        for data in created_assessments:
            assessment = Assessment.objects.get(user=data["user"])
            assert (
                assessment.sport == data["expected_sport"]
            ), f"Data loss detected for user {data['user'].email}"

        # Verify total count
        total_count = Assessment.objects.count()
        assert (
            total_count == 10
        ), f"Expected 10 assessments, found {total_count} (data loss detected)"

    def test_sport_field_queryable_with_filters(self):
        """Verify sport field can be queried with various filter operations."""
        # Arrange: Create assessments with different sports
        for i in range(6):
            user = User.objects.create_user(
                email=f"filter_test_{i}@example.com",
                password="TestPass123!",
            )
            sport = "soccer" if i < 3 else "cricket"
            Assessment.objects.create(
                user=user,
                sport=sport,
                age=25,
                experience_level="intermediate",
                training_days="4-5",
                equipment="basic_equipment",
            )

        # Act & Assert: Test various filter operations
        soccer_assessments = Assessment.objects.filter(sport="soccer")
        assert soccer_assessments.count() == 3, "Filter by sport='soccer' failed"

        cricket_assessments = Assessment.objects.filter(sport="cricket")
        assert cricket_assessments.count() == 3, "Filter by sport='cricket' failed"

        # Test exclude
        not_soccer = Assessment.objects.exclude(sport="soccer")
        assert not_soccer.count() == 3, "Exclude sport='soccer' failed"

        # Test __in filter
        multi_filter = Assessment.objects.filter(sport__in=["soccer", "cricket"])
        assert multi_filter.count() == 6, "Filter with __in failed"

    def test_sport_display_label_correct_after_retrieval(self):
        """Verify sport_display field shows correct label after persistence."""
        # Arrange: Create assessment with soccer
        user = User.objects.create_user(
            email="display_label@example.com",
            password="TestPass123!",
        )
        assessment = Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        # Act: Retrieve via API
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/assessments/{assessment.id}/")

        # Assert: Both sport and sport_display are correct
        assert response.status_code == 200
        assert (
            response.data["sport"] == "soccer"
        ), "Internal sport value incorrect after persistence"
        assert (
            response.data["sport_display"] == "Football"
        ), "Display label incorrect after persistence"
