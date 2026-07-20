import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai_assistant.app.assistant import answer_question
from ai_assistant.app.db import QueryExecutionError
from ai_assistant.app.question_guard import (
    UnsupportedQuestionError,
)
from ai_assistant.app.sql_guard import SQLValidationError


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Ecommerce AI Analytics Assistant",
    description=(
        "Experimental AI analytics assistant "
        "for ecommerce marts data."
    ),
    version="0.2.0",
)


class AskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500,
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-assistant",
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    try:
        return answer_question(request.question)

    except UnsupportedQuestionError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except SQLValidationError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except QueryExecutionError as error:
        logger.warning(
            "AI query execution failed: %s",
            error.database_message,
        )

        raise HTTPException(
            status_code=422,
            detail=error.public_message,
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        logger.exception(
            "Unexpected AI assistant error."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Asystent nie mógł przetworzyć pytania "
                "z powodu wewnętrznego błędu."
            ),
        )