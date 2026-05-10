from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
from tqdm import tqdm
from pathlib import Path

fake = Faker()

# =========================
# CONFIG
# =========================

CUSTOMERS_COUNT = 20_000
PRODUCTS_COUNT = 5_000
ORDERS_COUNT = 100_000

OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# CUSTOMERS
# =========================

def generate_customers():

    customers = []

    for customer_id in tqdm(range(1, CUSTOMERS_COUNT + 1), desc="Generating customers"):

        customers.append({
            "customer_id": customer_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "country": fake.country(),
            "city": fake.city(),
            "created_at": fake.date_time_between(
                start_date="-2y",
                end_date="now"
            )
        })

    df = pd.DataFrame(customers)

    df.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

# =========================
# PRODUCTS
# =========================

CATEGORIES = [
    "Electronics",
    "Fashion",
    "Sports",
    "Home",
    "Books",
    "Beauty"
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
    "Headphones"
]

def generate_products():

    products = []

    for product_id in tqdm(range(1, PRODUCTS_COUNT + 1), desc="Generating products"):

        products.append({
            "product_id": product_id,
            "product_name": f"{random.choice(PRODUCT_NAMES)} {product_id}",
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(5, 2000), 2),
            "stock_quantity": random.randint(0, 1000),
            "created_at": fake.date_time_between(
                start_date="-2y",
                end_date="now"
            )
        })

    df = pd.DataFrame(products)

    df.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False
    )

# =========================
# ORDERS
# =========================

ORDER_STATUSES = [
    "completed",
    "pending",
    "cancelled",
    "shipped"
]

def generate_orders():

    orders = []

    for order_id in tqdm(range(1, ORDERS_COUNT + 1), desc="Generating orders"):

        orders.append({
            "order_id": order_id,
            "customer_id": random.randint(1, CUSTOMERS_COUNT),
            "order_date": fake.date_time_between(
                start_date="-1y",
                end_date="now"
            ),
            "order_status": random.choice(ORDER_STATUSES),
            "total_amount": round(random.uniform(10, 5000), 2)
        })

    df = pd.DataFrame(orders)

    df.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("Starting dataset generation...")

    generate_customers()
    generate_products()
    generate_orders()

    print("Datasets generated successfully.")