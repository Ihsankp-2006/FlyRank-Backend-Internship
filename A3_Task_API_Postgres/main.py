from fastapi import FastAPI
from fastapi.responses import JSONResponse

from repository import (
    initialize_database,
    get_all_tasks,
    get_task
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
