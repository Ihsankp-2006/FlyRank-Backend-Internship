import sqlite3

from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI()

DATABASE = "tasks.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)

    task_count = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if task_count == 0:
        connection.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 0),
                ("Connect FastAPI to SQLite", 0),
                ("Test database persistence", 0)
            ]
        )

    connection.commit()
    connection.close()


initialize_database()


@app.get("/", summary="Get API information")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    connection = get_db_connection()

    rows = connection.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def get_task(task_id: int):
    connection = get_db_connection()

    row = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return dict(row)

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    connection = get_db_connection()

    cursor = connection.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title, 0)
    )

    connection.commit()

    task_id = cursor.lastrowid

    row = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return dict(row)

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: dict):
    if not task:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    connection = get_db_connection()

    row = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if row is None:
        connection.close()
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    if "title" in task:
        if not isinstance(task["title"], str) or not task["title"].strip():
            connection.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"}
            )

    if "done" in task:
        if not isinstance(task["done"], bool):
            connection.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be a boolean"}
            )

    if "title" not in task and "done" not in task:
        connection.close()
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request body"}
        )

    title = task.get("title", row["title"])
    done = task.get("done", bool(row["done"]))

    connection.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, int(done), task_id)
    )

    connection.commit()

    updated_row = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return dict(updated_row)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    connection = get_db_connection()

    cursor = connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return