import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    default_database = Path(app.instance_path) / "students.db"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-key"),
        DATABASE=os.environ.get("DATABASE_PATH", str(default_database)),
    )

    if test_config:
        app.config.update(test_config)

    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL UNIQUE
            )
            """
        )

    def get_students():
        with sqlite3.connect(app.config["DATABASE"]) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                "SELECT id, name, roll_number FROM students ORDER BY id DESC"
            ).fetchall()

    @app.get("/")
    def index():
        return render_template("index.html", students=get_students())

    @app.post("/students")
    def add_student():
        name = request.form.get("name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()

        if not name or not roll_number:
            flash("Please enter both a student name and roll number.", "error")
            return redirect(url_for("index"))

        if len(name) > 100 or len(roll_number) > 30:
            flash("Name must be 100 characters or fewer and roll number 30 or fewer.", "error")
            return redirect(url_for("index"))

        try:
            with sqlite3.connect(app.config["DATABASE"]) as connection:
                connection.execute(
                    "INSERT INTO students (name, roll_number) VALUES (?, ?)",
                    (name, roll_number),
                )
        except sqlite3.IntegrityError:
            flash("That roll number already exists. Please use a unique roll number.", "error")
            return redirect(url_for("index"))

        flash("Student added successfully.", "success")
        return redirect(url_for("index"))

    @app.post("/students/<int:student_id>/delete")
    def delete_student(student_id):
        with sqlite3.connect(app.config["DATABASE"]) as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE id = ?", (student_id,)
            )

        if cursor.rowcount == 0:
            flash("Student not found.", "error")
        else:
            flash("Student deleted successfully.", "success")
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        return jsonify(status="healthy"), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
