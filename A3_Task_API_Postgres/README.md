# Task API — PostgreSQL + Docker

A FastAPI Task API using PostgreSQL as the database, with the entire stack containerized using Docker Compose.

This project is the A3 continuation of the Task API:

- A1 — In-memory storage
- A2 — SQLite storage
- A3 — PostgreSQL in Docker

## Features

- FastAPI REST API
- PostgreSQL database
- Full CRUD operations
- Parameterized SQL queries
- Environment-based database configuration
- Dockerized FastAPI application
- Dockerized PostgreSQL database
- Persistent PostgreSQL volume
- Docker Compose one-command startup
- Automatic database table creation and seeding

## Project Structure

```text
A3_Task_API_Postgres/
├── .env
├── .env.example
├── Dockerfile
├── compose.yaml
├── db-screenshot.png
├── main.py
├── repository.py
├── requirements.txt
└── README.md
```

## Requirements

- Docker Desktop
- Git

Python and PostgreSQL do not need to be installed separately when using Docker Compose.

## Run the Application

Create the environment file from the example:

```powershell
cp .env.example .env
```

Start the complete stack:

```powershell
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Environment Variables

The application uses environment variables for database configuration.

Example `.env`:

```text
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev
POSTGRES_DB=tasks
DATABASE_URL=postgres://postgres:dev@localhost:5433/tasks
```

The actual `.env` file is ignored by Git.

`.env.example` is included in the repository so another developer can create their own `.env`.

Inside Docker Compose, FastAPI connects to PostgreSQL using the Docker service name:

```text
postgres://postgres:dev@db:5432/tasks
```

## API Endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/` | API information | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | Get all tasks | 200 |
| GET | `/tasks/{id}` | Get one task | 200 |
| POST | `/tasks` | Create a task | 201 |
| PUT | `/tasks/{id}` | Update a task | 200 |
| DELETE | `/tasks/{id}` | Delete a task | 204 |

Unknown task IDs return:

```json
{
  "error": "Task not found"
}
```

## Example Request

Create a task:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks -Method Post -ContentType "application/json" -Body '{"title":"Compose Persistence Test"}'
```

Example response:

```text
id title                     done
-- -----                     ----
4  Compose Persistence Test  False
```

## Database

The PostgreSQL database runs in its own Docker container.

The database uses a named Docker volume:

```text
taskdata
```

This allows database data to survive container recreation.

The application creates the `tasks` table automatically if it does not exist and seeds three initial tasks when the table is empty.

Database structure:

```text
tasks
├── id      SERIAL PRIMARY KEY
├── title   TEXT NOT NULL
└── done    BOOLEAN NOT NULL
```

## Database Screenshot

The PostgreSQL database was checked using:

```powershell
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

![PostgreSQL database contents](db-screenshot.png)

## Persistence Test

The API was tested with Docker Compose using the following process:

```text
docker compose up
        ↓
Create task
        ↓
docker compose down
        ↓
docker compose up
        ↓
Retrieve task
```

The created task remained available after restarting the Compose stack, confirming that the PostgreSQL data is stored in the persistent Docker volume.

## Stop the Application

Press:

```text
Ctrl + C
```

or run:

```powershell
docker compose down
```

`docker compose down` removes the containers and network but keeps the named database volume.

## Clean Clone

For a fresh clone:

```powershell
git clone https://github.com/Ihsankp-2006/FlyRank-Backend-Internship.git
cd FlyRank-Backend-Internship/A3_Task_API_Postgres
cp .env.example .env
docker compose up --build
```

The complete FastAPI + PostgreSQL stack can then be started with Docker Compose.

## Storage Evolution

| Assignment | Storage |
|---|---|
| A1 | In-memory Python list |
| A2 | SQLite |
| A3 | PostgreSQL in Docker |

A3 replaces SQLite with PostgreSQL while keeping the API behavior and CRUD endpoints consistent with the previous assignments.