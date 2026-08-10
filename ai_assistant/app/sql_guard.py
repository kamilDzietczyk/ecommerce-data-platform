import re


class SQLValidationError(ValueError):
    """Raised when generated SQL violates application security rules."""

    pass


ALLOWED_TABLES = {
    "marts.mart_daily_sales",
    "marts.mart_product_sales",
    "marts.mart_customer_value",
    "marts.dim_customers",
    "marts.dim_products",
    "marts.dim_dates",
    "marts.fct_orders",
    "marts.fct_order_items",
    "marts.mart_sales_forecast"
}


FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "merge",
    "copy",
    "call",
    "execute",
    "vacuum",
    "refresh",
    "lock",
    "into",
}


FORBIDDEN_EXPRESSIONS = {
    "information_schema",
    "pg_catalog",
    "pg_sleep",
    "pg_read_file",
    "pg_ls_dir",
    "lo_import",
    "lo_export",
    "dblink",
    "for update",
}


def extract_cte_names(query: str) -> set[str]:
    return set(
        re.findall(
            r"(?:\bwith\b|,)\s*"
            r"([a-z_][a-z0-9_]*)\s+as\s*\(",
            query,
            flags=re.IGNORECASE,
        )
    )

def remove_extract_expressions(query: str) -> str:
    return re.sub(
        r"\bextract\s*\(\s*[a-z_]+\s+from\s+"
        r"[a-z_][a-z0-9_.]*\s*\)",
        "extract_expression",
        query,
        flags=re.IGNORECASE,
    )

def extract_relations(query: str) -> list[str]:
    query_without_extract = remove_extract_expressions(query)

    return re.findall(
        r"\b(?:from|join)\s+"
        r"([a-z_][a-z0-9_.]*)",
        query_without_extract,
        flags=re.IGNORECASE,
    )


def validate_sql(query: str) -> str:
    if not query or not query.strip():
        raise SQLValidationError("Generated SQL is empty.")

    cleaned_query = query.strip()

    if cleaned_query.endswith(";"):
        cleaned_query = cleaned_query[:-1].strip()

    lowered_query = cleaned_query.lower()

    if ";" in cleaned_query:
        raise SQLValidationError(
            "Only one SQL statement is allowed."
        )

    if "--" in cleaned_query or "/*" in cleaned_query:
        raise SQLValidationError(
            "SQL comments are not allowed."
        )

    if not (
        lowered_query.startswith("select")
        or lowered_query.startswith("with")
    ):
        raise SQLValidationError(
            "Only SELECT or WITH queries are allowed."
        )

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(
            rf"\b{re.escape(keyword)}\b",
            lowered_query,
        ):
            raise SQLValidationError(
                f"Forbidden SQL keyword detected: {keyword}"
            )

    for expression in FORBIDDEN_EXPRESSIONS:
        if expression in lowered_query:
            raise SQLValidationError(
                f"Forbidden SQL expression detected: {expression}"
            )

    cte_names = extract_cte_names(lowered_query)
    relations = extract_relations(lowered_query)

    if not relations:
        raise SQLValidationError(
            "Query must read data from an allowed marts table."
        )

    for relation in relations:
        normalized_relation = relation.lower()

        if normalized_relation in cte_names:
            continue

        if normalized_relation not in ALLOWED_TABLES:
            raise SQLValidationError(
                f"Table is not allowed: {relation}"
            )

    return cleaned_query