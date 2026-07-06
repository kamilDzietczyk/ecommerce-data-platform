from psycopg2.extras import execute_values


def batch_insert(
    connection,
    table_name: str,
    columns: list,
    rows: list,
    page_size: int = 5000
):

    """
    Perform batch insert using execute_values.
    """

    cursor = connection.cursor()

    columns_sql = ", ".join(columns)

    query = f"""
        INSERT INTO {table_name}
        ({columns_sql})
        VALUES %s
    """

    execute_values(
        cursor,
        query,
        rows,
        page_size=page_size
    )

    connection.commit()

    cursor.close()

    print(f"Inserted {len(rows)} rows into {table_name}.")