import sqlite3
import random
from datetime import datetime, timedelta

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def main():
    database = "retail.db"

    sql_create_customers_table = """ CREATE TABLE IF NOT EXISTS customers (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        email text,
                                        city text,
                                        signup_date text
                                    ); """

    sql_create_products_table = """ CREATE TABLE IF NOT EXISTS products (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        category text,
                                        price real
                                    ); """

    sql_create_orders_table = """ CREATE TABLE IF NOT EXISTS orders (
                                        id integer PRIMARY KEY,
                                        customer_id integer NOT NULL,
                                        order_date text,
                                        total_amount real,
                                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                                    ); """

    sql_create_order_items_table = """ CREATE TABLE IF NOT EXISTS order_items (
                                        id integer PRIMARY KEY,
                                        order_id integer NOT NULL,
                                        product_id integer NOT NULL,
                                        quantity integer,
                                        price_at_purchase real,
                                        FOREIGN KEY (order_id) REFERENCES orders (id),
                                        FOREIGN KEY (product_id) REFERENCES products (id)
                                    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_customers_table)
        create_table(conn, sql_create_products_table)
        create_table(conn, sql_create_orders_table)
        create_table(conn, sql_create_order_items_table)

        # Seed Data
        cursor = conn.cursor()

        # Customers
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        for i in range(1, 101):
            name = f"Customer {i}"
            email = f"customer{i}@example.com"
            city = random.choice(cities)
            date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)", (name, email, city, date))

        # Products
        categories = ["Electronics", "Clothing", "Home", "Books"]
        for i in range(1, 21):
            name = f"Product {i}"
            category = random.choice(categories)
            price = round(random.uniform(10.0, 500.0), 2)
            cursor.execute("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", (name, category, price))

        # Orders & Order Items
        for i in range(1, 201):
            customer_id = random.randint(1, 100)
            order_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)", (customer_id, order_date, 0))
            order_id = cursor.lastrowid

            total_amount = 0
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product_id = random.randint(1, 20)
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                price = cursor.fetchone()[0]
                quantity = random.randint(1, 3)
                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)", (order_id, product_id, quantity, price))
                total_amount += price * quantity
            
            cursor.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (total_amount, order_id))

        conn.commit()
        print("Database seeded successfully.")
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
