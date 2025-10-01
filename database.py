import sqlite3

DB_NAME = "ordering_system.db"

# ==========================
# Database Initialization
# ==========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # === Create Products Table ===
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )
    """)

    # === Create Orders Table ===
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        total REAL NOT NULL,
        order_number TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # === Create Order Items Table ===
    c.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized with products, orders (with status), and order_items!")

# ==========================
# Product Functions
# ==========================
def get_products():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products")
    products = c.fetchall()
    conn.close()
    return products

def get_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock FROM products WHERE id=?", (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def add_product(name, price, stock):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()

def update_stock(product_id, quantity):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE products SET stock = stock - ? WHERE id=? AND stock >= ?", (quantity, product_id, quantity))
    conn.commit()
    conn.close()

# ==========================
# Order Functions
# ==========================
def add_order(customer_name, cart):
    """
    cart = [(product_id, quantity), ...]
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Calculate total
    total = 0
    for product_id, qty in cart:
        product = get_product(product_id)
        if product:
            total += product[2] * qty  # price * qty

    # Insert into orders
    c.execute("INSERT INTO orders (customer_name, total) VALUES (?, ?)", (customer_name, total))
    order_id = c.lastrowid

    # Insert order items
    for product_id, qty in cart:
        c.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                  (order_id, product_id, qty))
        update_stock(product_id, qty)

    conn.commit()
    conn.close()
    return order_id

def get_orders():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, customer_name, total, created_at FROM orders ORDER BY created_at DESC")
    orders = c.fetchall()
    conn.close()
    return orders

def get_order_details(order_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT p.name, oi.quantity, p.price, (oi.quantity * p.price) as subtotal
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,))
    details = c.fetchall()
    conn.close()
    return details

def create_order(cart, customer_name, order_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- calculate total ---
    total = 0.0
    for item in cart.values():
        total += item["price"] * item["quantity"]

    # --- insert into orders table ---
    cursor.execute(
        """
        INSERT INTO orders (customer_name, total, order_number, status)
        VALUES (?, ?, ?, ?)
        """,
        (customer_name, total, order_number, "pending"),
    )

    order_id = cursor.lastrowid

    # --- insert order items ---
    for product_id, item in cart.items():
        cursor.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (?, ?, ?)
            """,
            (order_id, int(product_id), item["quantity"]),
        )

    conn.commit()
    conn.close()
    return order_id

# ==========================
# Sample Data Seeder
# ==========================
def seed_products():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    sample_products = [
        ("Burger", 5.99, 20),
        ("Fries", 2.99, 50),
        ("Soda", 1.49, 100),
        ("Pizza", 8.99, 10)
    ]
    c.executemany("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", sample_products)
    conn.commit()
    conn.close()
    print("🍔 Sample products inserted!")

# ==========================
# Run directly
# ==========================
if __name__ == "__main__":
    init_db()