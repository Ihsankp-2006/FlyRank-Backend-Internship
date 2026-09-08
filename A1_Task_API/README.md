# FlyRank Backend Internship — Task API

A simple RESTful Task API built with Python and FastAPI as part of the FlyRank AI Internship Backend Track.

The API implements full CRUD operations using an in-memory list. No database or external storage is used.

## Features

- RESTful API built with FastAPI
- In-memory task storage
- Create, read, update, and delete tasks
- Request validation
- Proper HTTP status codes
- JSON error responses
- Interactive Swagger UI

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn

## Installation

Clone the repository:

```bash
git clone https://github.com/Ihsankp-2006/FlyRank-Backend-Internship.git
cd FlyRank-Backend-Internship

### Paste **this directly underneath**:

```markdown
Create a virtual environment:

```bash
python -m venv .venv

Activate the virtual environment on Windows:

.venv\Scripts\activate

Install the required dependencies:

pip install -r requirements.txt
Run the API

Start the server with:

python -m uvicorn main:app --reload

The API will be available at:

http://127.0.0.1:8000

API Endpoints
Method	Endpoint	Description	Status
GET	/	Get API information	200
GET	/health	Check API health	200
GET	/tasks	Get all tasks	200
GET	/tasks/{task_id}	Get a task by ID	200
POST	/tasks	Create a new task	201
PUT	/tasks/{task_id}	Update a task	200
DELETE	/tasks/{task_id}	Delete a task	204
Example Request

Create a new task:

{
  "title": "Buy milk"
}

Example response:

{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
Error Handling

The API returns the following status codes:

200 OK — Successful read or update
201 Created — Task successfully created
204 No Content — Task successfully deleted
400 Bad Request — Invalid request body
404 Not Found — Task ID does not exist

Example error response:

{
  "error": "Task 99 not found"
}
Example curl Output
$ curl.exe -i http://127.0.0.1:8000/tasks

HTTP/1.1 200 OK
date: Tue, 08 Sep 2026 18:16:42 GMT
server: uvicorn
content-length: 149
content-type: application/json

[{"id":1,"title":"Learn FastAPI","done":false},{"id":2,"title":"Build Task API","done":false},{"id":3,"title":"Push project to GitHub","done":false}]
Swagger UI

Interactive API documentation is available at:

http://127.0.0.1:8000/docs

Project Structure
FlyRank-Backend-Internship/
├── .gitignore
├── main.py
├── requirements.txt
├── README.md
└── swagger.png
Git Commit History

The project was developed incrementally through meaningful commits:

chore: initialize repository
feat: add hello FastAPI server
feat: add root and health endpoints
feat: add task read endpoints
feat: add task creation with validation
feat: add full task CRUD
docs: improve Swagger endpoint descriptions
docs: finalize project documentation