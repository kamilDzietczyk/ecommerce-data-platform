def generate_sql_with_mock(question: str) -> str:
    normalized_question = question.lower()

    if (
        "kategoria" in normalized_question
        or "category" in normalized_question
        or "według kategorii" in normalized_question
    ):
        return """
        SELECT
            category,
            SUM(total_sales) AS total_sales
        FROM marts.mart_product_sales
        GROUP BY category
        ORDER BY total_sales DESC
        LIMIT 10
        """

    if (
        "produkt" in normalized_question
        or "product" in normalized_question
        or "top products" in normalized_question
        or "najlepiej" in normalized_question
    ):
        return """
        SELECT
            product_name,
            category,
            total_quantity,
            total_sales
        FROM marts.mart_product_sales
        ORDER BY total_sales DESC
        LIMIT 10
        """

    if (
        "klient" in normalized_question
        or "customer" in normalized_question
        or "lifetime" in normalized_question
    ):
        return """
        SELECT
            customer_id,
            first_name,
            last_name,
            country,
            city,
            total_orders,
            lifetime_value,
            average_order_value
        FROM marts.mart_customer_value
        ORDER BY lifetime_value DESC
        LIMIT 10
        """

    return """
    SELECT
        sales_date,
        total_revenue,
        total_orders,
        average_order_value
    FROM marts.mart_daily_sales
    ORDER BY sales_date
    LIMIT 30
    """