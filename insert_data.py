import os
import psycopg2
from faker import Faker

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

TABLES = ["customers", "products", "orders"]

fake = Faker()

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                price DECIMAL(10,2)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INT REFERENCES customers(id),
                product_id INT REFERENCES products(id),
                quantity INT
            );
        """)
        conn.commit()
    print("Tables created.")

def insert_random_data(conn, num_customers=5, num_products=5, num_orders=10):
    with conn.cursor() as cur:
        # Insert customers
        for _ in range(num_customers):
            cur.execute(
                "INSERT INTO customers (name, email) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (fake.name(), fake.unique.email())
            )
        # Insert products
        for _ in range(num_products):
            cur.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s);",
                (fake.word(), round(fake.pydecimal(left_digits=3, right_digits=2, positive=True), 2))
            )
        conn.commit()

        # Insert orders
        cur.execute("SELECT id FROM customers;")
        customer_ids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT id FROM products;")
        product_ids = [row[0] for row in cur.fetchall()]

        for _ in range(num_orders):
            cur.execute(
                "INSERT INTO orders (customer_id, product_id, quantity) VALUES (%s, %s, %s);",
                (fake.random_element(customer_ids), fake.random_element(product_ids), fake.random_int(1, 5))
            )
        conn.commit()
    print("Random data inserted.")

def main():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    create_tables(conn)
    insert_random_data(conn)
    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()
