# A6 – Put an LLM Behind Your API

## Overview

A FastAPI-based support ticket classification API that accepts customer messages and returns structured, validated JSON using a locally hosted LLM through Ollama.

The API classifies each support ticket by:

- **Category:** `billing`, `technical`, `account`, or `general`
- **Priority:** `low`, `medium`, or `high`
- **Recommended action:** `reply`, `investigate`, or `escalate`
- **Confidence score:** A value between 0 and 1
- **Reason:** A short explanation for the classification

## Tech Stack

- Python 3
- FastAPI
- Pydantic
- OpenAI-compatible Python client
- Ollama
- Gemma 3 1B

## Project Structure

```text
A6_Task_API_LLM/
├── evals/
│   ├── cases.json
│   ├── results.json
│   └── run_eval.py
├── prompts/
│   └── support_ticket_v1.txt
├── src/
│   ├── llm/
│   │   └── hello.py
│   ├── main.py
│   └── schemas.py
├── .env.example
├── .gitignore
├── JOB-CARD.md
├── requirements.txt
└── README.md
```

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ihsankp-2006/FlyRank-Backend-Internship.git
cd FlyRank-Backend-Internship/A6_Task_API_LLM
```

### 2. Activate the Virtual Environment

The repository uses a shared virtual environment in its root directory.

For Windows PowerShell:

```powershell
..\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file using the example configuration:

```powershell
Copy-Item .env.example .env
```

Configure the following values in `.env`:

```env
LLM_BASE_URL=http://localhost:11434/v1/
LLM_API_KEY=ollama
LLM_MODEL=gemma3:1b
LLM_STUB=0
LLM_ENABLED=true
```

### 5. Start Ollama

Ensure Ollama is installed and the model is available:

```bash
ollama pull gemma3:1b
```

### 6. Start the API

From the `A6_Task_API_LLM` directory:

```bash
uvicorn src.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

**GET** `/health`

Checks whether the API is running.

### Classify Support Ticket

**POST** `/classify`

Accepts a customer support message and returns a structured classification.

**Request:**

```json
{
  "message": "I was charged twice for my subscription."
}
```

**Example Response:**

```json
{
  "category": "billing",
  "priority": "medium",
  "recommended_action": "investigate",
  "confidence": 0.95,
  "reason": "The customer reports being charged twice."
}
```

The exact classification may vary depending on the model response.

### PowerShell Request Example

```powershell
$body = @{
    message = "I was charged twice for my subscription."
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/classify" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Reliability and Error Handling

The API includes the following reliability mechanisms:

- Input validation is performed before calling the model.
- Invalid input returns HTTP 400.
- Pydantic validates the model output against the defined schema.
- Invalid model output receives one repair attempt.
- If the repaired output is still invalid, the request returns HTTP 422 and is logged for quarantine.
- Provider timeouts and retryable server errors use bounded retries.
- Non-retryable client errors such as HTTP 400, 401, and 403 are not retried.
- Provider failures are returned as HTTP 503 or 502, depending on the failure.
- Model calls have a 30-second timeout.

## Stub Mode and Kill Switch

The API supports deterministic fallback classification without calling the LLM.

**Enable stub mode:**

```env
LLM_STUB=1
```

**Disable LLM access using the kill switch:**

```env
LLM_ENABLED=false
```

**Restore real model inference:**

```env
LLM_STUB=0
LLM_ENABLED=true
```

## Logging

Each model call logs operational information, including:

- Model name
- Prompt version
- Prompt and completion token counts
- Request duration
- Estimated cost
- Repair count
- Classification mode

The local Ollama configuration reports an estimated model-call cost of `$0.0`.

## Evaluation

The evaluation suite is located in the `evals/` directory.

Run the evaluation while the API server is running:

```powershell
cd evals
python run_eval.py
```

### Evaluation Results

| Metric | Result |
|---|---:|
| Total test cases | 8 |
| Correct classifications | 8 |
| Overall accuracy | 100.00% |
| Prompt version | support_ticket_v1 |
| Evaluation date | 2026-11-06 |

**Category-wise results:**

| Category | Correct | Total |
|---|---:|---:|
| Billing | 2 | 2 |
| Technical | 2 | 2 |
| Account | 2 | 2 |
| General | 2 | 2 |

Results are saved in `evals/results.json`.

The reported score reflects this eight-case evaluation set and is not a guarantee of production accuracy.

## Security and Configuration

- `.env` is excluded from Git.
- `.env.example` provides non-secret configuration defaults.
- User messages are passed separately from the system prompt.
- Model output is validated before being returned by the API.
- The classifier is designed for a narrow support-ticket classification task, not general-purpose conversation.

## Prompt Versioning

The current prompt is stored in:

```text
prompts/support_ticket_v1.txt
```

**Current prompt version:** `support_ticket_v1`

## Internship Assignment

**FlyRank AI Internship Program**

**Assignment A6:** Put an LLM Behind Your API.
