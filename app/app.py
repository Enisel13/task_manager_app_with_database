import os
import mysql.connector

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# DATABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", ""),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "tasks_db")
    )


# HOME
@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        app_version=os.getenv("APP_VERSION", "dev")
    )


# HEALTH CHECK
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# DATABASE READINESS CHECK
@app.route("/ready", methods=["GET"])
def readiness():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200

    except Exception:
        app.logger.exception("Database readiness check failed")
        return jsonify({"status": "not ready"}), 503


# ABOUT
@app.route("/about", methods=["GET"])
def about():
    return jsonify({
        "application": "Task Manager",
        "description": "A Flask application connected to MySQL"
    })


# WHO AM I
@app.route("/whoami", methods=["GET"])
def whoami():
    return jsonify({
        "hostname": os.getenv(
            "POD_NAME",
            os.getenv("HOSTNAME", "local")
        )
    })


# CREATE TASK
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    description = data.get("description", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            INSERT INTO tasks (title, description)
            VALUES (%s, %s)
            """,
            (title.strip(), description.strip())
        )

        task_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            """
            SELECT id, title, description, completed, created_at
            FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )

        task = cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

    return jsonify(task), 201


# READ ALL TASKS
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, title, description, completed, created_at
            FROM tasks
            ORDER BY created_at DESC
            """
        )

        tasks = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return jsonify(tasks), 200


# READ ONE TASK
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, title, description, completed, created_at
            FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )

        task = cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task), 200


# UPDATE TASK
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    allowed_fields = {"title", "description", "completed"}

    if not set(data).issubset(allowed_fields):
        return jsonify({"error": "Unsupported field"}), 400

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 400

    if "description" in data and not isinstance(data["description"], str):
        return jsonify({"error": "Description must be a string"}), 400

    if "completed" in data and not isinstance(data["completed"], bool):
        return jsonify({"error": "Completed must be true or false"}), 400

    updates = []
    values = []

    for field in ("title", "description", "completed"):
        if field in data:
            value = data[field]

            if field in ("title", "description"):
                value = value.strip()

            updates.append(f"{field} = %s")
            values.append(value)

    values.append(task_id)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            f"""
            UPDATE tasks
            SET {", ".join(updates)}
            WHERE id = %s
            """,
            values
        )

        conn.commit()

        cursor.execute(
            """
            SELECT id, title, description, completed, created_at
            FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )

        task = cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task), 200


# DELETE TASK
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s",
            (task_id,)
        )

        deleted = cursor.rowcount > 0
        conn.commit()

    finally:
        cursor.close()
        conn.close()

    if not deleted:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "message": "Task deleted successfully",
        "id": task_id
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)