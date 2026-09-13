import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]

            if task_count == 0:
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    [
                        ("Learn FastAPI", False),
                        ("Connect FastAPI to PostgreSQL", False),
                        ("Test database persistence", False)
                    ]
                )

        connection.commit()


def get_all_tasks():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "done": row[2]
                }
                for row in rows
            ]


def get_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "title": row[1],
                "done": row[2]
            }


def create_task(title):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING *
                """,
                (title, False)
            )

            row = cursor.fetchone()

        connection.commit()

        return {
            "id": row[0],
            "title": row[1],
            "done": row[2]
        }


def update_task(task_id, title, done):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                """,
                (title, done, task_id)
            )

            if cursor.rowcount == 0:
                return None

            cursor.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,)
            )

            row = cursor.fetchone()

        connection.commit()

        return {
            "id": row[0],
            "title": row[1],
            "done": row[2]
        }


def delete_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,)
            )

            deleted = cursor.rowcount > 0

        connection.commit()

        return deleted