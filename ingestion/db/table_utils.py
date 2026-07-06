def truncate_table(
    connection,
    table_name: str
):

    """
    Truncate table before ingestion.
    """

    cursor = connection.cursor()

    query = f"TRUNCATE TABLE {table_name};"

    cursor.execute(query)

    connection.commit()

    cursor.close()

    print(f"Table truncated: {table_name}")