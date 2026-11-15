kubectl exec -i deployment/task-manager-app -- python - <<'PY'
import os
import mysql.connector

conn = mysql.connector.connect(
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ.get("MYSQL_PORT", "3306")),
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    database=os.environ["MYSQL_DATABASE"],
)

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        completed BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

tasks = [
    ("Set up project repository", "Create the repository and add the initial project files.", True),
    ("Configure the database", "Set up the database and verify the application connection.", True),
    ("Build the task API", "Implement endpoints to create, read, update, and delete tasks.", False),
    ("Add input validation", "Validate task titles and descriptions before saving them.", False),
]

cursor.executemany(
    "INSERT INTO tasks (title, description, completed) VALUES (%s, %s, %s)",
    tasks,
)
conn.commit()

print(f"Inserted {cursor.rowcount} tasks.")

cursor.close()
conn.close()
PY