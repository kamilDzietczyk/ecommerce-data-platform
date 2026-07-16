FORBIDDEN_KEYWORDS = [
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
]

FORBIDDEN_SCHEMAS = [
    "raw.",
    "staging.",
    "public.",
]


def validate_sql(query: str) -> str:
    cleaned_query = query.strip()

    if cleaned_query.endswith(";"):
        cleaned_query = cleaned_query[:-1].strip()

    lowered_query = cleaned_query.lower()

    if ";" in cleaned_query:
        raise ValueError("Only a single SQL statement is allowed.")

    if not (
        lowered_query.startswith("select")
        or lowered_query.startswith("with")
    ):
        raise ValueError("Only SELECT queries are allowed.")

    for keyword in FORBIDDEN_KEYWORDS:
        if f"{keyword} " in lowered_query or f"{keyword}\n" in lowered_query:
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    for schema in FORBIDDEN_SCHEMAS:
        if schema in lowered_query:
            raise ValueError(f"Access to schema is forbidden: {schema}")

    if "marts." not in lowered_query:
        raise ValueError("Query must use only marts schema.")

    return cleaned_query