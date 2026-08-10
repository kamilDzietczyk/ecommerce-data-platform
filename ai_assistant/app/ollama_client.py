import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

from ai_assistant.app.schema_context import (
    MARTS_SCHEMA_CONTEXT,
)


load_dotenv(override=False)


# ============================================================
# ENVIRONMENT
# ============================================================

def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value


# ============================================================
# MODEL RESPONSE CLEANUP
# ============================================================

def clean_model_response(response_text: str) -> str:
    cleaned_text = response_text.strip()

    cleaned_text = re.sub(
        r"^```(?:sql)?\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s*```$",
        "",
        cleaned_text,
    )

    return cleaned_text.strip()


# ============================================================
# OLLAMA HTTP CLIENT
# ============================================================

def call_ollama(
    messages: list[dict[str, str]],
) -> str:

    base_url = get_required_env(
        "OLLAMA_BASE_URL"
    ).rstrip("/")

    model = get_required_env(
        "OLLAMA_MODEL"
    )

    timeout_seconds = float(
        os.getenv(
            "OLLAMA_TIMEOUT_SECONDS",
            "180",
        )
    )

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    try:
        with httpx.Client(
            timeout=timeout_seconds
        ) as client:

            response = client.post(
                f"{base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Check whether Ollama is running "
            "and whether OLLAMA_BASE_URL is correct."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            "Ollama did not respond within "
            f"{timeout_seconds} seconds."
        ) from error

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            "Ollama returned HTTP "
            f"{error.response.status_code}: "
            f"{error.response.text}"
        ) from error

    try:
        response_data = response.json()

    except ValueError as error:
        raise RuntimeError(
            "Ollama returned an invalid JSON response."
        ) from error

    generated_content = (
        response_data
        .get("message", {})
        .get("content", "")
    )

    if not generated_content.strip():
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return generated_content.strip()


# ============================================================
# SQL GENERATION
# ============================================================

def generate_sql_with_ollama(
    question: str,
) -> str:

    system_prompt = f"""
You are a PostgreSQL analytics SQL generator.

Generate exactly one safe, read-only SQL query.

FORECASTING RULES:

- Future total revenue questions must use
  marts.mart_sales_forecast.
- Use forecast_month to filter the requested future month.
- Use predicted_revenue as the forecasted value.
- Never derive future revenue by extrapolating historical
  tables yourself.
- Never invent future values.
- Product-level forecasts are not available.
- Category-level forecasts are not available.
- Customer-level forecasts are not available.

HISTORICAL RULES:

- Historical questions must use historical marts,
  fact tables or dimensions.
- Never use marts.mart_sales_forecast for historical
  actual-sales questions.
- For historical monthly revenue analysis, prefer
  marts.mart_monthly_sales.
- For historical daily analysis, prefer
  marts.mart_daily_sales.
- For historical product analysis without a date filter,
  prefer marts.mart_product_sales.
- For historical product analysis with a date filter,
  join fct_order_items with fct_orders and dim_products.

GENERAL RULES:

- Return SQL only.
- Do not provide explanations.
- Do not use Markdown code blocks.
- Generate exactly one SQL query.
- Use only SELECT or WITH.
- Use only tables from the marts schema listed below.
- Use only columns explicitly listed below.
- Never access raw.
- Never access staging.
- Never access public.
- Never access forecast directly.
- Never access information_schema.
- Never access pg_catalog.
- Never use INSERT.
- Never use UPDATE.
- Never use DELETE.
- Never use DROP.
- Never use ALTER.
- Never use TRUNCATE.
- Never use CREATE.
- Never use GRANT.
- Never use REVOKE.
- Never use COPY.
- Never use CALL.
- Never use EXECUTE.
- Never invent tables or columns.
- Verify every alias.column reference before returning SQL.
- Prefer date ranges instead of EXTRACT when possible.
- Limit detailed result sets to a maximum of 50 rows.
- Use PostgreSQL syntax.

AVAILABLE SCHEMA:

{MARTS_SCHEMA_CONTEXT}
""".strip()

    generated_sql = call_ollama(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ]
    )

    return clean_model_response(
        generated_sql
    )


# ============================================================
# SQL REPAIR
# ============================================================

def build_repair_hint(
    failed_sql: str,
    database_error: str,
) -> str:

    diagnostic_text = (
        f"{failed_sql}\n{database_error}"
    ).lower()

    if (
        "oi.order_date" in diagnostic_text
        or (
            "order_date"
            in database_error.lower()
            and "fct_order_items"
            in failed_sql.lower()
        )
    ):
        return """
The failed query incorrectly uses oi.order_date.

Mandatory correction:
- order_date exists only in marts.fct_orders.
- Join marts.fct_order_items AS oi
  with marts.fct_orders AS o
  using o.order_id = oi.order_id.
- Filter dates using o.order_date.
- Never use oi.order_date.
""".strip()

    if (
        "forecast_month" in diagnostic_text
        or "predicted_revenue" in diagnostic_text
    ):
        return """
For future total revenue:
- Use marts.mart_sales_forecast.
- Use forecast_month for the requested month.
- Use predicted_revenue as the forecasted value.
- Do not calculate future revenue from historical tables.
""".strip()

    return (
        "Verify that every alias.column reference exists "
        "in the table represented by that alias. "
        "Use only tables and columns explicitly listed "
        "in the schema context."
    )


def repair_sql_with_ollama(
    question: str,
    failed_sql: str,
    database_error: str,
) -> str:

    system_prompt = f"""
You are a PostgreSQL analytics SQL expert.

A previous SQL query failed in PostgreSQL.
Generate exactly one corrected, safe, read-only SQL query.

FORECASTING RULES:

- Future total revenue questions must use
  marts.mart_sales_forecast.
- Use forecast_month and predicted_revenue.
- Never invent future values.
- Never calculate forecasts directly from historical tables.
- Product/category/customer forecasting is not available.

GENERAL RULES:

- Return SQL only.
- Do not explain the correction.
- Do not use Markdown code blocks.
- Use only SELECT or WITH.
- Use only tables from the marts schema listed below.
- Use only columns listed in the schema context.
- Follow the listed table relationships.
- Never access raw.
- Never access staging.
- Never access public.
- Never access forecast directly.
- Never access information_schema.
- Never access pg_catalog.
- Never use INSERT.
- Never use UPDATE.
- Never use DELETE.
- Never use DROP.
- Never use ALTER.
- Never use TRUNCATE.
- Never use CREATE.
- Never use GRANT.
- Never use REVOKE.
- Never use COPY.
- Never use CALL.
- Never use EXECUTE.
- Verify every alias.column reference.
- Limit detailed result sets to a maximum of 50 rows.
- Use PostgreSQL syntax.

AVAILABLE SCHEMA:

{MARTS_SCHEMA_CONTEXT}
""".strip()

    repair_hint = build_repair_hint(
        failed_sql=failed_sql,
        database_error=database_error,
    )

    repair_prompt = f"""
Original user question:
{question}

Failed SQL:
{failed_sql}

PostgreSQL error:
{database_error}

Mandatory correction hint:
{repair_hint}

Generate a corrected query.

Important:
- Do not return the failed SQL unchanged.
- Verify every table alias.
- Verify every column reference.
- Follow the mandatory correction hint.
- Return SQL only.
""".strip()

    repaired_sql = call_ollama(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": repair_prompt,
            },
        ]
    )

    return clean_model_response(
        repaired_sql
    )


# ============================================================
# RESULT TYPE
# ============================================================

def detect_result_type(
    sql_query: str,
) -> str:

    normalized_sql = sql_query.lower()

    if (
        "marts.mart_sales_forecast"
        in normalized_sql
    ):
        return "FORECAST"

    return "HISTORICAL"


# ============================================================
# RESULT SUMMARY
# ============================================================

def summarize_result_with_ollama(
    question: str,
    sql_query: str,
    rows: list[dict[str, Any]],
) -> str:

    if not rows:
        return (
            "Nie znaleziono danych "
            "odpowiadających temu pytaniu."
        )

    result_type = detect_result_type(
        sql_query
    )

    # Nie wysyłamy modelowi nieograniczonej
    # liczby rekordów.
    result_sample = rows[:20]

    serialized_result = json.dumps(
        result_sample,
        ensure_ascii=False,
        default=str,
    )

    system_prompt = """
You are an ecommerce data analyst.

Your task is to explain the provided database result.

GENERAL RULES:

- Answer in the same language as the user's question.
- Base your answer only on the provided query result.
- Do not invent causes.
- Do not invent values.
- Do not invent trends that are not visible in the result.
- Mention the most important values.
- Keep the answer concise: maximum three sentences.
- Do not use Markdown tables.
- Do not describe SQL or implementation details.

HISTORICAL DATA RULES:

If Data type is HISTORICAL:
- The values represent historical actual analytical data.
- Never call historical values forecasts or predictions.
- Never say that historical actual revenue is predicted.
- Answer directly using the historical result.

FORECAST DATA RULES:

If Data type is FORECAST:
- Clearly say that the value is a forecast or prediction.
- Do not present predicted revenue as a certainty.
- Use wording such as "prognozowana sprzedaż" when answering
  in Polish.
- Mention the forecasting model if model_name is available.
- Do not claim that forecasted revenue has already occurred.
""".strip()

    user_prompt = f"""
User question:
{question}

Data type:
{result_type}

Executed SQL:
{sql_query}

Number of returned rows:
{len(rows)}

Query result sample:
{serialized_result}

Answer the user's question using only this information.
""".strip()

    return call_ollama(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )