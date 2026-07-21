import math
import random
from calendar import monthrange
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker
from tqdm import tqdm


# =========================
# REPRODUCIBILITY
# =========================

RANDOM_SEED = 42

rng = random.Random(RANDOM_SEED)

Faker.seed(RANDOM_SEED)
fake = Faker()
fake.seed_instance(RANDOM_SEED)


# =========================
# CONFIG
# =========================

CUSTOMERS_COUNT = 20_000
PRODUCTS_COUNT = 5_000
ORDERS_COUNT = 100_000

DATA_START_DATE = datetime(
    year=2023,
    month=6,
    day=1,
)

DATA_END_DATE = datetime(
    year=2026,
    month=5,
    day=31,
    hour=23,
    minute=59,
    second=59,
)

CUSTOMER_CREATED_START_DATE = datetime(
    year=2021,
    month=1,
    day=1,
)

CUSTOMER_CREATED_END_DATE = (
    DATA_START_DATE
    - timedelta(seconds=1)
)

PRODUCT_CREATED_START_DATE = datetime(
    year=2021,
    month=1,
    day=1,
)

PRODUCT_CREATED_END_DATE = (
    DATA_START_DATE
    - timedelta(seconds=1)
)

ANNUAL_ORDER_GROWTH_RATE = 0.08
ANNUAL_PRICE_GROWTH_RATE = 0.03

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================
# SEASONALITY
# =========================

MONTHLY_SEASONAL_MULTIPLIERS = {
    1: 0.92,
    2: 0.88,
    3: 0.96,
    4: 1.00,
    5: 1.04,
    6: 1.02,
    7: 0.94,
    8: 0.97,
    9: 1.02,
    10: 1.10,
    11: 1.30,
    12: 1.45,
}


# =========================
# CUSTOMERS
# =========================

def generate_customers() -> pd.DataFrame:
    customers = []

    for customer_id in tqdm(
        range(1, CUSTOMERS_COUNT + 1),
        desc="Generating customers",
    ):
        customers.append(
            {
                "customer_id": customer_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.unique.email(),
                "country": fake.country(),
                "city": fake.city(),
                "created_at": fake.date_time_between(
                    start_date=CUSTOMER_CREATED_START_DATE,
                    end_date=CUSTOMER_CREATED_END_DATE,
                ),
            }
        )

    dataframe = pd.DataFrame(customers)

    dataframe.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False,
    )

    return dataframe


# =========================
# PRODUCTS
# =========================

CATEGORIES = [
    "Electronics",
    "Fashion",
    "Sports",
    "Home",
    "Books",
    "Beauty",
]

PRODUCT_NAMES = [
    "Laptop",
    "Keyboard",
    "Monitor",
    "Sneakers",
    "T-Shirt",
    "Backpack",
    "Protein Bar",
    "Coffee Maker",
    "Notebook",
    "Headphones",
]


def generate_products() -> pd.DataFrame:
    products = []

    for product_id in tqdm(
        range(1, PRODUCTS_COUNT + 1),
        desc="Generating products",
    ):
        products.append(
            {
                "product_id": product_id,
                "product_name": (
                    f"{rng.choice(PRODUCT_NAMES)} "
                    f"{product_id}"
                ),
                "category": rng.choice(CATEGORIES),
                "price": round(
                    rng.uniform(5, 2000),
                    2,
                ),
                "stock_quantity": rng.randint(
                    0,
                    1000,
                ),
                "created_at": fake.date_time_between(
                    start_date=PRODUCT_CREATED_START_DATE,
                    end_date=PRODUCT_CREATED_END_DATE,
                ),
            }
        )

    dataframe = pd.DataFrame(products)

    dataframe.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False,
    )

    return dataframe


# =========================
# TRANSACTION CONFIG
# =========================

ORDER_STATUSES = [
    "completed",
    "pending",
    "cancelled",
    "shipped",
]

ORDER_STATUS_WEIGHTS = [
    60,
    10,
    10,
    20,
]

PAYMENT_METHODS = [
    "credit_card",
    "paypal",
    "bank_transfer",
    "apple_pay",
    "google_pay",
]

SHIPMENT_PROVIDERS = [
    "DHL",
    "FedEx",
    "UPS",
    "DPD",
    "InPost",
]


# =========================
# MONTHLY ORDER PLAN
# =========================

def get_month_starts() -> list[datetime]:
    return [
        timestamp.to_pydatetime()
        for timestamp in pd.date_range(
            start=DATA_START_DATE,
            end=DATA_END_DATE,
            freq="MS",
        )
    ]


def build_monthly_order_plan() -> list[tuple[datetime, int]]:
    months = get_month_starts()

    monthly_weights = []

    for month_index, month_start in enumerate(months):
        trend_multiplier = (
            1 + ANNUAL_ORDER_GROWTH_RATE
        ) ** (month_index / 12)

        seasonal_multiplier = (
            MONTHLY_SEASONAL_MULTIPLIERS[
                month_start.month
            ]
        )

        random_monthly_noise = rng.uniform(
            0.97,
            1.03,
        )

        weight = (
            trend_multiplier
            * seasonal_multiplier
            * random_monthly_noise
        )

        monthly_weights.append(weight)

    total_weight = sum(monthly_weights)

    raw_monthly_counts = [
        ORDERS_COUNT
        * weight
        / total_weight
        for weight in monthly_weights
    ]

    monthly_counts = [
        math.floor(raw_count)
        for raw_count in raw_monthly_counts
    ]

    remaining_orders = (
        ORDERS_COUNT
        - sum(monthly_counts)
    )

    fractional_order = sorted(
        range(len(raw_monthly_counts)),
        key=lambda index: (
            raw_monthly_counts[index]
            - monthly_counts[index]
        ),
        reverse=True,
    )

    for month_index in fractional_order[
        :remaining_orders
    ]:
        monthly_counts[month_index] += 1

    return list(
        zip(
            months,
            monthly_counts,
        )
    )


def random_datetime_in_month(
    month_start: datetime,
) -> datetime:
    last_day = monthrange(
        month_start.year,
        month_start.month,
    )[1]

    return datetime(
        year=month_start.year,
        month=month_start.month,
        day=rng.randint(1, last_day),
        hour=rng.randint(0, 23),
        minute=rng.randint(0, 59),
        second=rng.randint(0, 59),
    )


# =========================
# PRICES
# =========================

def calculate_unit_price(
    base_price: float,
    month_index: int,
) -> float:
    price_growth_multiplier = (
        1 + ANNUAL_PRICE_GROWTH_RATE
    ) ** (month_index / 12)

    price_noise = rng.uniform(
        0.95,
        1.05,
    )

    calculated_price = (
        base_price
        * price_growth_multiplier
        * price_noise
    )

    return round(
        max(calculated_price, 0.01),
        2,
    )


# =========================
# PAYMENT
# =========================

def get_payment_status(
    order_status: str,
) -> str:
    if order_status in {
        "completed",
        "shipped",
    }:
        return "paid"

    if order_status == "pending":
        return "pending"

    return rng.choices(
        population=[
            "failed",
            "refunded",
        ],
        weights=[
            70,
            30,
        ],
        k=1,
    )[0]


# =========================
# SHIPMENT
# =========================

def build_shipment_data(
    order_status: str,
    order_date: datetime,
) -> dict:
    if order_status == "cancelled":
        return {
            "shipment_status": "cancelled",
            "shipment_provider": None,
            "shipped_date": None,
            "delivered_date": None,
        }

    provider = rng.choice(
        SHIPMENT_PROVIDERS
    )

    if order_status == "pending":
        return {
            "shipment_status": "processing",
            "shipment_provider": provider,
            "shipped_date": None,
            "delivered_date": None,
        }

    shipped_date = (
        order_date
        + timedelta(
            days=rng.randint(1, 3),
            hours=rng.randint(0, 12),
        )
    )

    if order_status == "shipped":
        return {
            "shipment_status": "shipped",
            "shipment_provider": provider,
            "shipped_date": shipped_date,
            "delivered_date": None,
        }

    delivered_date = (
        shipped_date
        + timedelta(
            days=rng.randint(1, 7),
            hours=rng.randint(0, 12),
        )
    )

    return {
        "shipment_status": "delivered",
        "shipment_provider": provider,
        "shipped_date": shipped_date,
        "delivered_date": delivered_date,
    }


# =========================
# ORDERS, ITEMS, PAYMENTS,
# SHIPMENTS
# =========================

def generate_transactions(
    products_dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    product_prices = (
        products_dataframe
        .set_index("product_id")["price"]
        .to_dict()
    )

    monthly_order_plan = (
        build_monthly_order_plan()
    )

    orders = []
    order_items = []
    payments = []
    shipments = []

    order_id = 1
    order_item_id = 1

    progress_bar = tqdm(
        total=ORDERS_COUNT,
        desc="Generating transactions",
    )

    for month_index, (
        month_start,
        orders_in_month,
    ) in enumerate(monthly_order_plan):

        for _ in range(orders_in_month):
            order_date = random_datetime_in_month(
                month_start
            )

            customer_id = rng.randint(
                1,
                CUSTOMERS_COUNT,
            )

            order_status = rng.choices(
                population=ORDER_STATUSES,
                weights=ORDER_STATUS_WEIGHTS,
                k=1,
            )[0]

            items_count = rng.randint(
                1,
                5,
            )

            selected_product_ids = rng.sample(
                range(
                    1,
                    PRODUCTS_COUNT + 1,
                ),
                items_count,
            )

            total_amount = 0.0

            for product_id in selected_product_ids:
                quantity = rng.randint(
                    1,
                    3,
                )

                unit_price = calculate_unit_price(
                    base_price=product_prices[
                        product_id
                    ],
                    month_index=month_index,
                )

                line_total = round(
                    quantity * unit_price,
                    2,
                )

                total_amount += line_total

                order_items.append(
                    {
                        "order_item_id": (
                            order_item_id
                        ),
                        "order_id": order_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                    }
                )

                order_item_id += 1

            total_amount = round(
                total_amount,
                2,
            )

            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "order_date": order_date,
                    "order_status": order_status,
                    "total_amount": total_amount,
                }
            )

            payment_status = get_payment_status(
                order_status
            )

            payment_date = (
                order_date
                + timedelta(
                    hours=rng.randint(0, 48)
                )
            )

            payments.append(
                {
                    "payment_id": order_id,
                    "order_id": order_id,
                    "payment_method": rng.choice(
                        PAYMENT_METHODS
                    ),
                    "payment_status": payment_status,
                    "payment_date": payment_date,
                    "payment_amount": total_amount,
                }
            )

            shipment_data = (
                build_shipment_data(
                    order_status=order_status,
                    order_date=order_date,
                )
            )

            shipments.append(
                {
                    "shipment_id": order_id,
                    "order_id": order_id,
                    **shipment_data,
                }
            )

            order_id += 1
            progress_bar.update(1)

    progress_bar.close()

    orders_dataframe = pd.DataFrame(
        orders
    )

    order_items_dataframe = pd.DataFrame(
        order_items
    )

    payments_dataframe = pd.DataFrame(
        payments
    )

    shipments_dataframe = pd.DataFrame(
        shipments
    )

    orders_dataframe.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False,
    )

    order_items_dataframe.to_csv(
        OUTPUT_DIR / "order_items.csv",
        index=False,
    )

    payments_dataframe.to_csv(
        OUTPUT_DIR / "payments.csv",
        index=False,
    )

    shipments_dataframe.to_csv(
        OUTPUT_DIR / "shipments.csv",
        index=False,
    )

    return (
        orders_dataframe,
        order_items_dataframe,
        payments_dataframe,
        shipments_dataframe,
    )


# =========================
# VALIDATION SUMMARY
# =========================

def print_generation_summary(
    orders_dataframe: pd.DataFrame,
) -> None:
    summary_dataframe = (
        orders_dataframe
        .assign(
            order_month=(
                orders_dataframe["order_date"]
                .dt.to_period("M")
                .astype(str)
            )
        )
        .groupby(
            "order_month",
            as_index=False,
        )
        .agg(
            total_orders=(
                "order_id",
                "count",
            ),
            total_revenue=(
                "total_amount",
                "sum",
            ),
        )
    )

    print()
    print("Generated sales history")
    print("=" * 60)

    print(
        summary_dataframe.to_string(
            index=False,
            formatters={
                "total_revenue": (
                    lambda value: (
                        f"{value:,.2f}"
                    )
                )
            },
        )
    )

    print()
    print(
        "First order date: "
        f"{orders_dataframe['order_date'].min()}"
    )

    print(
        "Last order date: "
        f"{orders_dataframe['order_date'].max()}"
    )

    print(
        "Number of months: "
        f"{len(summary_dataframe)}"
    )

    print(
        "Total orders: "
        f"{len(orders_dataframe)}"
    )


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print(
        "Starting dataset generation..."
    )

    generate_customers()

    products_dataframe = (
        generate_products()
    )

    (
        orders_dataframe,
        _,
        _,
        _,
    ) = generate_transactions(
        products_dataframe
    )

    print_generation_summary(
        orders_dataframe
    )

    print(
        "Datasets generated successfully."
    )