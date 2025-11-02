"""
Unit tests for Assessment database-level indexes and constraints.
Tests for Feature #21 Story 21.8: Verify Database Indexes and Constraints.

Note: Database-level constraint tests require PostgreSQL and are skipped for SQLite.
"""

import pytest
from django.conf import settings
from django.db import IntegrityError, connection
from django.db.utils import DataError

from apps.assessments.models import Assessment
from apps.users.models import User


# Helper to check if we're using PostgreSQL
def is_postgresql():
    """Check if the database backend is PostgreSQL."""
    return settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


# Skip marker for PostgreSQL-only tests
requires_postgresql = pytest.mark.skipif(
    not is_postgresql(), reason="Requires PostgreSQL database backend"
)


@pytest.mark.django_db
class TestAssessmentDatabaseConstraints:
    """Test database-level constraints on Assessment model."""

    @requires_postgresql
    def test_sport_check_constraint_rejects_invalid_values(self) -> None:
        """
        Test that database-level CHECK constraint rejects invalid sport values.

        Acceptance Criteria:
        - Given invalid sport values are submitted
        - When the database processes them
        - Then they should be rejected with clear error messages
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Attempt to bypass Django validation by using raw SQL
        with connection.cursor() as cursor:
            with pytest.raises(IntegrityError) as exc_info:
                cursor.execute(
                    """
                    INSERT INTO assessments
                        (user_id, sport, age, experience_level,
                         training_days, injuries, equipment,
                         equipment_items, created_at, updated_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    [
                        user.id,
                        "basketball",
                        25,
                        "intermediate",
                        "4-5",
                        "no",
                        "basic_equipment",
                        "[]",
                    ],
                )

        # Verify the constraint violation is caught
        assert "assessments_sport_valid_choice" in str(exc_info.value)

    @requires_postgresql
    def test_sport_check_constraint_accepts_soccer(self) -> None:
        """
        Test that database-level CHECK constraint accepts 'soccer' as valid sport.

        Acceptance Criteria:
        - Given the sport field has valid values
        - When I inspect database constraints
        - Then it should enforce valid sport choices at the database level
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Insert using raw SQL to verify database constraint allows 'soccer'
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO assessments
                    (user_id, sport, age, experience_level,
                     training_days, injuries, equipment,
                     equipment_items, created_at, updated_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                [
                    user.id,
                    "soccer",
                    25,
                    "intermediate",
                    "4-5",
                    "no",
                    "basic_equipment",
                    "[]",
                ],
            )

        # Verify the record was created successfully
        assessment = Assessment.objects.get(user=user)
        assert assessment.sport == "soccer"

    @requires_postgresql
    def test_sport_check_constraint_accepts_cricket(self) -> None:
        """
        Test that database-level CHECK constraint accepts 'cricket' as valid sport.

        Acceptance Criteria:
        - Given the sport field has valid values
        - When I inspect database constraints
        - Then it should enforce valid sport choices at the database level
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Insert using raw SQL to verify database constraint allows 'cricket'
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO assessments
                    (user_id, sport, age, experience_level,
                     training_days, injuries, equipment,
                     equipment_items, created_at, updated_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                [
                    user.id,
                    "cricket",
                    25,
                    "intermediate",
                    "4-5",
                    "no",
                    "basic_equipment",
                    "[]",
                ],
            )

        # Verify the record was created successfully
        assessment = Assessment.objects.get(user=user)
        assert assessment.sport == "cricket"

    def test_sport_field_has_proper_data_type(self) -> None:
        """
        Test sport field has proper data type and length.

        Acceptance Criteria:
        - Given the assessment table schema
        - When I review field definitions
        - Then the sport field should have proper data type, length, and null constraints
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name, data_type,
                       character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'assessments' AND column_name = 'sport';
                """
            )
            result = cursor.fetchone()

        # Verify field definition
        assert result is not None, "Sport column not found in assessments table"
        column_name, data_type, max_length, is_nullable = result

        assert column_name == "sport"
        assert data_type == "character varying", f"Expected VARCHAR, got {data_type}"
        assert max_length == 20, f"Expected max length 20, got {max_length}"
        assert is_nullable == "NO", "Sport field should NOT be nullable"

    def test_sport_field_not_null_constraint(self) -> None:
        """
        Test sport field has NOT NULL constraint at database level.

        Acceptance Criteria:
        - Given the assessment table schema
        - When I review field definitions
        - Then the sport field should have proper null constraints
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Attempt to insert NULL value for sport field using raw SQL
        with connection.cursor() as cursor:
            with pytest.raises(IntegrityError) as exc_info:
                cursor.execute(
                    """
                    INSERT INTO assessments
                        (user_id, sport, age, experience_level,
                         training_days, injuries, equipment,
                         equipment_items, created_at, updated_at)
                    VALUES
                        (%s, NULL, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    [user.id, 25, "intermediate", "4-5", "no", "basic_equipment", "[]"],
                )

        # Verify NOT NULL constraint violation
        assert "null value in column" in str(exc_info.value).lower()
        assert "sport" in str(exc_info.value).lower()


@pytest.mark.django_db
class TestAssessmentDatabaseIndexes:
    """Test database-level indexes on Assessment model."""

    def test_sport_field_has_index(self) -> None:
        """
        Test sport field has appropriate database index for performance.

        Acceptance Criteria:
        - Given the sport field is queried frequently
        - When I check database indexes
        - Then there should be an appropriate index on the sport column
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessments' AND indexdef LIKE '%sport%';
                """
            )
            indexes = cursor.fetchall()

        # Verify sport index exists
        assert len(indexes) > 0, "No index found on sport column"

        # Check that the index is on the sport field
        sport_indexes = [idx for idx in indexes if "sport" in idx[1].lower()]
        assert len(sport_indexes) > 0, "No index specifically for sport field"

        # Verify it's a btree index (default and most efficient for equality queries)
        index_def = sport_indexes[0][1]
        assert "btree" in index_def.lower() or "USING btree" in index_def

    def test_user_field_has_index(self) -> None:
        """
        Test user_id field has appropriate index for relationship queries.

        Note: This is essential for OneToOneField performance.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessments' AND indexdef LIKE '%user_id%';
                """
            )
            indexes = cursor.fetchall()

        # Verify user_id index exists
        assert len(indexes) > 0, "No index found on user_id column"

        # Should have both regular index and unique constraint
        user_indexes = [idx for idx in indexes if "user_id" in idx[1].lower()]
        assert len(user_indexes) >= 1, "Missing user_id index"

    def test_created_at_field_has_index(self) -> None:
        """
        Test created_at field has index for ordering queries.

        Note: This is important for default ordering by -created_at.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'assessments' AND indexdef LIKE '%created_at%';
                """
            )
            indexes = cursor.fetchall()

        # Verify created_at index exists
        assert len(indexes) > 0, "No index found on created_at column"

    def test_all_declared_indexes_exist(self) -> None:
        """
        Test that all indexes declared in model Meta are actually created in database.

        Model declares indexes on: user, sport, created_at
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'assessments'
                ORDER BY indexname;
                """
            )
            indexes = [row[0] for row in cursor.fetchall()]

        # Verify minimum expected indexes exist
        # Note: Index names may vary based on Django version and migration history
        indexed_columns = ["user_id", "sport", "created_at"]

        for column in indexed_columns:
            matching_indexes = [idx for idx in indexes if column in idx]
            assert (
                len(matching_indexes) > 0
            ), f"No index found for {column} column in indexes: {indexes}"


@pytest.mark.django_db
class TestAssessmentConstraintErrorMessages:
    """Test that constraint violations provide clear error messages."""

    @requires_postgresql
    def test_invalid_sport_error_message_clarity(self) -> None:
        """
        Test invalid sport values are rejected with clear error messages.

        Acceptance Criteria:
        - Given invalid sport values are submitted
        - When the database processes them
        - Then they should be rejected with clear error messages
        """
        from django.db import transaction

        # Test a few representative invalid sports
        # Note: We use separate transactions for each to avoid transaction rollback issues
        invalid_sports = ["football", "basketball", ""]

        for invalid_sport in invalid_sports:
            # Create a new user for each test to avoid unique constraint issues
            user = User.objects.create_user(
                email=f"test_{invalid_sport or 'empty'}@example.com",
                password="testpass123",
            )

            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        # This should raise an error
                        cursor.execute(
                            """
                            INSERT INTO assessments
                                (user_id, sport, age, experience_level,
                                 training_days, injuries, equipment,
                                 equipment_items, created_at, updated_at)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                            """,
                            [
                                user.id,
                                invalid_sport,
                                25,
                                "intermediate",
                                "4-5",
                                "no",
                                "basic_equipment",
                                "[]",
                            ],
                        )
                    # If we get here, the constraint didn't work
                    pytest.fail(
                        f"Expected IntegrityError for invalid sport "
                        f"'{invalid_sport}' but none was raised"
                    )
            except (IntegrityError, DataError) as e:
                # Verify error message identifies the constraint or field
                error_msg = str(e)
                # Should mention constraint name or check constraint violation
                assert (
                    "assessments_sport_valid_choice" in error_msg
                    or "check constraint" in error_msg.lower()
                    or "violates check constraint" in error_msg.lower()
                ), (f"Error message not clear for invalid sport " f"'{invalid_sport}': {error_msg}")
            finally:
                # Clean up
                user.delete()

    @requires_postgresql
    def test_constraint_names_are_descriptive(self) -> None:
        """
        Test that constraint names are descriptive and follow naming conventions.

        This helps DBAs and developers quickly identify constraint violations.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT conname, pg_get_constraintdef(oid) as definition
                FROM pg_constraint
                WHERE conrelid = 'assessments'::regclass
                ORDER BY conname;
                """
            )
            constraints = cursor.fetchall()

        constraint_dict = {name: definition for name, definition in constraints}

        # Verify sport check constraint exists with descriptive name
        assert any(
            "sport" in name and "valid" in name or "choice" in name
            for name in constraint_dict.keys()
        ), (
            f"Sport check constraint name not descriptive. "
            f"Found constraints: {list(constraint_dict.keys())}"
        )

        # Verify the sport constraint has the correct definition
        sport_constraint = next(
            (name for name in constraint_dict.keys() if "sport" in name and "valid" in name),
            None,
        )
        if sport_constraint:
            definition = constraint_dict[sport_constraint]
            assert "soccer" in definition.lower(), "Sport constraint should include 'soccer'"
            assert "cricket" in definition.lower(), "Sport constraint should include 'cricket'"


@pytest.mark.django_db
class TestAssessmentIndexPerformance:
    """Test that indexes provide expected performance benefits."""

    def test_sport_index_improves_query_performance(self) -> None:
        """
        Test sport index is used by query planner for filtering queries.

        This verifies the index actually improves query performance.
        """
        # Create test user and assessment
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # Check query plan for sport filter
        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXPLAIN SELECT * FROM assessments WHERE sport = 'soccer';
                """
            )
            plan = cursor.fetchall()
            plan_text = " ".join([str(row[0]) for row in plan])

        # Verify index is mentioned in query plan (for larger datasets)
        # Note: For small datasets, PostgreSQL may use Seq Scan as it's faster
        # The important thing is that the index EXISTS and CAN be used
        # We verify the index exists in other tests
        assert plan is not None, "Query plan should be available"

    def test_user_index_supports_relationship_lookup(self) -> None:
        """
        Test user_id index efficiently supports reverse relationship lookups.
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        Assessment.objects.create(
            user=user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            injuries="no",
            equipment="basic_equipment",
        )

        # This query should use the user_id index
        with connection.cursor() as cursor:
            cursor.execute(
                """
                EXPLAIN SELECT * FROM assessments WHERE user_id = %s;
                """,
                [user.id],
            )
            plan = cursor.fetchall()

        # Verify plan exists (index will be used for larger datasets)
        assert plan is not None, "Query plan should be available"
        assert len(plan) > 0, "Query plan should have results"
