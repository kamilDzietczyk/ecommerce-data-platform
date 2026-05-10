from ingestion.datasets.customers_loader import load_customers
from ingestion.datasets.products_loader import load_products
from ingestion.datasets.orders_loader import load_orders


def test_loaders():

    customers_df = load_customers()
    print(customers_df.head())

    products_df = load_products()
    print(products_df.head())

    orders_df = load_orders()
    print(orders_df.head())


if __name__ == "__main__":

    test_loaders()