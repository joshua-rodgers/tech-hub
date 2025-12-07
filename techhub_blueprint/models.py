import sqlite3
import os

def get_db_path():
    """Get the path to the database file"""
    return os.path.join(os.path.dirname(__file__), 'techhub.db')

def init_db():
    """Initialize database with schema and seed data"""
    db_path = get_db_path()

    # Only create if doesn't exist
    if os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT DEFAULT 'default.jpg',
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create customers table (VULNERABLE - stores credit cards in plain text)
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            full_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            credit_card TEXT,
            cvv TEXT,
            expiration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create admins table
    cursor.execute('''
        CREATE TABLE admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total REAL,
            status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Create order_items table
    cursor.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Insert default admin (VULNERABLE - plain text password)
    cursor.execute(
        "INSERT INTO admins (username, password) VALUES (?, ?)",
        ('admin', 'admin123')
    )

    # Insert sample products
    products = [
        ('RTX 4090 Gaming PC', 'High-performance gaming desktop with the latest NVIDIA RTX 4090 graphics card, Intel Core i9 processor, 32GB RAM, and 2TB SSD storage.', 2847.63, 'Computers', 'default.jpg', 5),
        ('Intel Core i9 Processor', '13th Gen Intel Core i9-13900K Desktop Processor 24 cores (8 P-cores + 16 E-cores) with integrated graphics.', 589.99, 'Components', 'default.jpg', 15),
        ('Gaming Laptop', '17-inch gaming laptop with RTX 4060, Intel i7, 16GB RAM, 1TB SSD. Perfect for gaming on the go!', 1499.99, 'Computers', 'default.jpg', 8),
        ('Mechanical Keyboard', 'RGB mechanical gaming keyboard with Cherry MX switches, programmable keys, and aluminum frame.', 149.99, 'Accessories', 'default.jpg', 25),
        ('Gaming Mouse', 'Wireless gaming mouse with 20,000 DPI sensor, customizable RGB lighting, and 8 programmable buttons.', 79.99, 'Accessories', 'default.jpg', 30),
        ('32GB DDR5 RAM', 'High-speed DDR5 RAM kit (2x16GB) running at 6000MHz. Perfect for gaming and content creation.', 189.99, 'Components', 'default.jpg', 20),
        ('2TB NVMe SSD', 'Ultra-fast NVMe M.2 SSD with read speeds up to 7000MB/s. Ideal for your OS and games.', 199.99, 'Storage', 'default.jpg', 12),
        ('4K Gaming Monitor', '32-inch 4K UHD gaming monitor with 144Hz refresh rate, 1ms response time, and HDR support.', 699.99, 'Monitors', 'default.jpg', 7),
        ('Gaming Headset', 'Surround sound gaming headset with noise-canceling microphone and comfortable memory foam ear cushions.', 129.99, 'Accessories', 'default.jpg', 18),
        ('Webcam HD', '1080p HD webcam with auto-focus, built-in microphone, and wide-angle lens. Perfect for streaming!', 89.99, 'Accessories', 'default.jpg', 22),
        ('Graphics Tablet', 'Professional graphics tablet with 8192 pressure levels and battery-free stylus. Great for digital artists!', 249.99, 'Accessories', 'default.jpg', 10),
        ('USB Hub', '7-port USB 3.0 hub with individual power switches and LED indicators. Expand your connectivity!', 34.99, 'Accessories', 'default.jpg', 40),
        ('Laptop Cooling Pad', 'Laptop cooling pad with 5 quiet fans, adjustable height, and dual USB ports.', 39.99, 'Accessories', 'default.jpg', 35),
        ('Cable Management Kit', 'Complete cable management solution with clips, sleeves, and ties. Keep your setup organized!', 24.99, 'Accessories', 'default.jpg', 50)
    ]

    cursor.executemany(
        "INSERT INTO products (name, description, price, category, image_url, stock) VALUES (?, ?, ?, ?, ?, ?)",
        products
    )

    # Insert sample customer (VULNERABLE - plain text password and credit card)
    cursor.execute(
        '''INSERT INTO customers
           (username, password, email, full_name, address, city, state, zip_code, credit_card, cvv, expiration)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        ('patricia.sandoval', 'password123', 'psandoval@email.com', 'Patricia Sandoval',
         '742 Evergreen Terrace', 'Springfield', 'IL', '62704',
         '4532-1234-5678-9010', '847', '03/27')
    )

    conn.commit()
    conn.close()

    print("[TechHub] Database initialized successfully!")
    print("[TechHub] Default admin credentials: admin / admin123")
    print("[TechHub] Sample customer: patricia.sandoval / password123")
