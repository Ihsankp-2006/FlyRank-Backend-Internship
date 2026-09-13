from fastapi import FastAPI
from fastapi.responses import JSONResponse

from repository import (
    initialize_database,
    get_all_tasks,
    get_task,
    create_task,
    update_task,
    delete_task
)

app = FastAPI()

initialize_database()


@app.get("/", summary="Get API information")
def root():
    return {
        "name": "Task API",
        "version": "3.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="Get all tasks")
def read_tasks():
    return get_all_tasks()


@app.get("/tasks/{task_id}", summary="Get a task by ID")
def read_task(task_id: int):
    task = get_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
def add_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    return create_task(title)


@app.put("/tasks/{task_id}", summary="Update a task")
def edit_task(task_id: int, task: dict):
    existing_task = get_task(task_id)

    if existing_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    if not task:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    title = task.get("title", existing_task["title"])
    done = task.get("done", existing_task["done"])

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    if not isinstance(done, bool):
        return JSONResponse(
            status_code=400,
            content={"error": "Done must be a boolean"}
        )

    return update_task(task_id, title, done)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def remove_task(task_id: int):
    deleted = delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return