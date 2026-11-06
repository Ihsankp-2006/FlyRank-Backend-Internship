import json
import logging
import os
import time
from pathlib import Path

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
    InternalServerError,
)
from pydantic import ValidationError

from src.schemas import TicketInput, TicketClassification

# Configuration
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticket-classifier")

app = FastAPI(title="A6 Support Ticket Classifier", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid input",
            "details": exc.errors(),
        },
    )

PROMPT_VERSION = "support_ticket_v1"
PROMPT_PATH = ROOT / "prompts" / f"{PROMPT_VERSION}.txt"
PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

MODEL = os.getenv("LLM_MODEL", "gemma3:1b")
RETRY_LIMIT = 3
TIMEOUT_SECONDS = 30


def make_client():
    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/"),
        api_key=os.getenv("LLM_API_KEY", "ollama"),
        timeout=TIMEOUT_SECONDS,
        max_retries=0,
    )


def request_json(messages):
    """Request JSON from Ollama with bounded retries."""
    client = make_client()

    for attempt in range(RETRY_LIMIT):
        started = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=300,
            )

            duration_ms = int((time.perf_counter() - started) * 1000)
            content = response.choices[0].message.content or ""
            usage = response.usage

            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            logger.info(
                "llm_call model=%s prompt_version=%s "
                "prompt_tokens=%s completion_tokens=%s "
                "duration_ms=%s estimated_cost_usd=0.0",
                MODEL,
                PROMPT_VERSION,
                prompt_tokens,
                completion_tokens,
                duration_ms,
            )

            return content

        except (APITimeoutError, APIConnectionError, RateLimitError,
                InternalServerError) as exc:
            logger.warning(
                "Retryable error=%s attempt=%d/%d",
                type(exc).__name__,
                attempt + 1,
                RETRY_LIMIT,
            )

            if attempt == RETRY_LIMIT - 1:
                raise

        except APIStatusError as exc:
            if exc.status_code != 429 and exc.status_code < 500:
                # Do not retry authentication or invalid-request errors.
                raise

            logger.warning(
                "Retryable HTTP status=%s attempt=%d/%d",
                exc.status_code,
                attempt + 1,
                RETRY_LIMIT,
            )

            if attempt == RETRY_LIMIT - 1:
                raise

        if attempt < RETRY_LIMIT - 1:
            time.sleep(0.5 * (2 ** attempt))

    raise RuntimeError("LLM request failed after retries")


def classify_stub(message: str) -> TicketClassification:
    text = message.lower()

    if any(word in text for word in [
        "refund", "payment", "invoice", "charged", "billing"
    ]):
        category = "billing"
    elif any(word in text for word in [
        "login", "password", "account", "locked", "access"
    ]):
        category = "account"
    elif any(word in text for word in [
        "error", "bug", "crash", "outage", "not working"
    ]):
        category = "technical"
    else:
        category = "general"

    urgent = any(word in text for word in [
        "unauthorized", "hacked", "security breach",
        "everyone is down", "urgent"
    ])

    priority = (
        "high" if urgent
        else "medium" if category != "general"
        else "low"
    )

    action = (
        "escalate" if urgent
        else "investigate" if category == "technical"
        else "reply"
    )

    return TicketClassification(
        category=category,
        priority=priority,
        recommended_action=action,
        confidence=0.75 if category != "general" else 0.55,
        reason="Deterministic stub classification; no LLM call was made.",
    )


def classify_with_llm(message: str):
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": message},
    ]

    for repair_count in range(2):
        content = request_json(messages)

        try:
            data = json.loads(content)
            result = TicketClassification.model_validate(data)

            logger.info(
                "classification_success prompt_version=%s repair_count=%d",
                PROMPT_VERSION,
                repair_count,
            )

            return result

        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning(
                "Invalid output repair_count=%d error=%s",
                repair_count,
                type(exc).__name__,
            )

            if repair_count == 1:
                raise

            messages = [
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Return ONLY a corrected JSON object matching "
                        "the required schema. No markdown or explanation.\n"
                        f"Customer message:\n{message}\n"
                        f"Invalid response:\n{content}"
                    ),
                },
            ]

    raise RuntimeError("Classification failed")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=TicketClassification)
def classify_ticket(payload: TicketInput):
    started = time.perf_counter()

    stub_mode = os.getenv("LLM_STUB", "1").lower() in {
        "1", "true", "yes"
    }
    llm_enabled = os.getenv("LLM_ENABLED", "true").lower() in {
        "1", "true", "yes"
    }

    # Deterministic fallback when stub mode is active or LLM is disabled.
    if stub_mode or not llm_enabled:
        result = classify_stub(payload.message)

        mode = "stub" if stub_mode else "disabled_fallback"

        logger.info(
            "classification mode=%s prompt_version=%s duration_ms=%d",
            mode,
            PROMPT_VERSION,
            int((time.perf_counter() - started) * 1000),
        )

        return result

    try:
        result = classify_with_llm(payload.message)

    except (json.JSONDecodeError, ValidationError) as exc:
        logger.error(
            "Output quarantined after repair failure error=%s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=422,
            detail="Model output failed validation after one repair attempt.",
        ) from exc

    except (APITimeoutError, APIConnectionError,
            RateLimitError, InternalServerError) as exc:
        logger.exception("LLM temporarily unavailable")
        raise HTTPException(
            status_code=503,
            detail="Classification service temporarily unavailable.",
        ) from exc

    except APIStatusError as exc:
        logger.exception("LLM provider returned an error")
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected classification failure")
        raise HTTPException(
            status_code=502,
            detail="Classification service failed.",
        ) from exc

    logger.info(
        "classification mode=llm prompt_version=%s "
        "model=%s total_duration_ms=%d",
        PROMPT_VERSION,
        MODEL,
        int((time.perf_counter() - started) * 1000),
    )

    return result
