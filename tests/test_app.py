import sqlite3

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(tmp_path / "test_students.db"),
        }
    )
    yield test_app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_page_shows_empty_state(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Student Management" in response.data
    assert b"No students have been added yet." in response.data


def test_add_student(client):
    response = client.post(
        "/students",
        data={"name": "Asha Sharma", "roll_number": "CS101"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Asha Sharma" in response.data
    assert b"CS101" in response.data
    assert b"Student added successfully." in response.data


def test_student_records_are_displayed(client):
    client.post("/students", data={"name": "Ravi Kumar", "roll_number": "ME202"})

    response = client.get("/")

    assert response.status_code == 200
    assert b"Ravi Kumar" in response.data
    assert b"ME202" in response.data
    assert b"1 total" in response.data


def test_student_records_persist_when_app_is_recreated(tmp_path):
    database = str(tmp_path / "persistent_students.db")
    first_app = create_app({"TESTING": True, "DATABASE": database})
    first_app.test_client().post(
        "/students", data={"name": "Nina Patel", "roll_number": "IT606"}
    )

    second_app = create_app({"TESTING": True, "DATABASE": database})
    response = second_app.test_client().get("/")

    assert response.status_code == 200
    assert b"Nina Patel" in response.data
    assert b"IT606" in response.data


def test_delete_student(client):
    client.post("/students", data={"name": "Meera Das", "roll_number": "EC303"})
    with client.application.app_context():
        with sqlite3.connect(client.application.config["DATABASE"]) as connection:
            student_id = connection.execute(
                "SELECT id FROM students WHERE roll_number = ?", ("EC303",)
            ).fetchone()[0]

    response = client.post(
        f"/students/{student_id}/delete", follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Meera Das" not in response.data
    assert b"Student deleted successfully." in response.data


@pytest.mark.parametrize(
    ("name", "roll_number"),
    [("", "CS404"), ("   ", "CS405"), ("A student", ""), ("A student", "   ")],
)
def test_add_student_rejects_missing_fields(client, name, roll_number):
    response = client.post(
        "/students",
        data={"name": name, "roll_number": roll_number},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please enter both a student name and roll number." in response.data
    assert b"1 total" not in response.data


def test_add_student_rejects_duplicate_roll_number(client):
    client.post("/students", data={"name": "First Student", "roll_number": "CS505"})

    response = client.post(
        "/students",
        data={"name": "Another Student", "roll_number": "CS505"},
        follow_redirects=True,
    )

    assert b"That roll number already exists." in response.data
    assert b"First Student" in response.data
    assert b"Another Student" not in response.data


def test_add_student_rejects_values_over_character_limits(client):
    response = client.post(
        "/students",
        data={"name": "N" * 101, "roll_number": "R" * 31},
        follow_redirects=True,
    )

    assert b"Name must be 100 characters or fewer" in response.data
    assert b"1 total" not in response.data


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
