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

PAYMENT_METHODS = [
    "credit_card",
    "paypal",
    "bank_transfer",
    "apple_pay",
    "google_pay"
]

PAYMENT_STATUSES = [
    "paid",
    "pending",
    "failed",
    "refunded"
]

SHIPMENT_STATUSES = [
    "processing",
    "shipped",
    "delivered",
    "cancelled"
]

SHIPMENT_PROVIDERS = [
    "DHL",
    "FedEx",
    "UPS",
    "DPD",
    "InPost"
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

def generate_order_items():

    order_items = []

    order_item_id = 1

    for order_id in tqdm(range(1, ORDERS_COUNT + 1), desc="Generating order items"):

        items_count = random.randint(1, 5)

        used_products = set()

        for _ in range(items_count):

            product_id = random.randint(1, PRODUCTS_COUNT)

            while product_id in used_products:
                product_id = random.randint(1, PRODUCTS_COUNT)

            used_products.add(product_id)

            quantity = random.randint(1, 3)

            unit_price = round(random.uniform(5, 2000), 2)

            order_items.append({
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price
            })

            order_item_id += 1

    df = pd.DataFrame(order_items)

    df.to_csv(
        OUTPUT_DIR / "order_items.csv",
        index=False
    )

def generate_payments():

    payments = []

    for payment_id in tqdm(range(1, ORDERS_COUNT + 1), desc="Generating payments"):

        payment_status = random.choices(
            PAYMENT_STATUSES,
            weights=[75, 10, 10, 5]
        )[0]

        payment_amount = round(random.uniform(10, 5000), 2)

        payments.append({
            "payment_id": payment_id,
            "order_id": payment_id,
            "payment_method": random.choice(PAYMENT_METHODS),
            "payment_status": payment_status,
            "payment_date": fake.date_time_between(
                start_date="-1y",
                end_date="now"
            ),
            "payment_amount": payment_amount
        })

    df = pd.DataFrame(payments)

    df.to_csv(
        OUTPUT_DIR / "payments.csv",
        index=False
    )

def generate_shipments():

    shipments = []

    for shipment_id in tqdm(range(1, ORDERS_COUNT + 1), desc="Generating shipments"):

        shipment_status = random.choice(SHIPMENT_STATUSES)

        shipped_date = None
        delivered_date = None

        if shipment_status in ["shipped", "delivered"]:

            shipped_date = fake.date_time_between(
                start_date="-1y",
                end_date="now"
            )

        if shipment_status == "delivered":

            delivered_date = shipped_date + timedelta(
                days=random.randint(1, 10)
            )

        provider = None

        if shipment_status != "cancelled":
            provider = random.choice(SHIPMENT_PROVIDERS)

        shipments.append({
            "shipment_id": shipment_id,
            "order_id": shipment_id,
            "shipment_status": shipment_status,
            "shipment_provider": provider,
            "shipped_date": shipped_date,
            "delivered_date": delivered_date
        })

    df = pd.DataFrame(shipments)

    df.to_csv(
        OUTPUT_DIR / "shipments.csv",
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
    generate_order_items()
    generate_payments()
    generate_shipments()

    print("Datasets generated successfully.")