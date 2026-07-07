from ingestion.pipelines.load_customers import run_pipeline as load_customers
from ingestion.pipelines.load_products import run_pipeline as load_products
from ingestion.pipelines.load_orders import run_pipeline as load_orders
from ingestion.pipelines.load_order_items import run_pipeline as load_order_items
from ingestion.pipelines.load_payments import run_pipeline as load_payments
from ingestion.pipelines.load_shipments import run_pipeline as load_shipments


def run_all_ingestion():

    print("Starting full ecommerce ingestion...")

    load_customers()
    load_products()
    load_orders()
    load_order_items()
    load_payments()
    load_shipments()

    print("Full ecommerce ingestion completed successfully.")


if __name__ == "__main__":

    run_all_ingestion()