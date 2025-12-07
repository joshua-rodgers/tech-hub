# TechHub Electronics - Technical Specification
## Vulnerable Flask Blueprint for SQL Injection Training

---

## PROJECT OVERVIEW

Create a self-contained Flask blueprint simulating "TechHub Electronics," an early 2000s e-commerce site with intentional SQL injection vulnerabilities for educational cybersecurity training. The application must match the technical details from the Marcus Chen case study.

---

## DIRECTORY STRUCTURE

```
/techhub_blueprint/
├── __init__.py
├── routes.py
├── models.py
├── utils.py
├── techhub.db (created at runtime)
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── cart.js
│   └── uploads/
│       └── products/
│           ├── default.jpg
│           └── [product images]
└── templates/
    ├── base.html
    ├── index.html
    ├── products.html
    ├── product_detail.html
    ├── cart.html
    ├── checkout.html
    ├── order_confirmation.html
    ├── login.html
    ├── register.html
    ├── account.html
    ├── order_history.html
    └── admin/
        ├── admin_base.html
        ├── dashboard.html
        ├── products.html
        ├── add_product.html
        ├── edit_product.html
        ├── customers.html
        ├── add_customer.html
        └── bulk_upload.html
```

---

## DATABASE SCHEMA (SQLite3)

### Tables with Exact Column Names from Case Study

```sql
-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT,
    image_url TEXT DEFAULT 'default.jpg',
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table (VULNERABLE - stores credit cards in plain text)
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
);

-- Admins table
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    total REAL,
    status TEXT DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Order items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Seed Data

**Default Admin:**
- Username: `admin`
- Password: `admin123` (plain text)

**Sample Products (10-15 items):**
- RTX 4090 Gaming PC - $2,847.63
- Intel Core i9 Processor - $589.99
- Gaming Laptop - $1,499.99
- Mechanical Keyboard - $149.99
- Gaming Mouse - $79.99
- 32GB DDR5 RAM - $189.99
- 2TB NVMe SSD - $199.99
- 4K Gaming Monitor - $699.99
- Gaming Headset - $129.99
- Webcam HD - $89.99
- Graphics Tablet - $249.99
- USB Hub - $34.99
- Laptop Cooling Pad - $39.99
- Cable Management Kit - $24.99

**Sample Customer:**
- Username: `patricia.sandoval`
- Email: `psandoval@email.com`
- Full Name: `Patricia Sandoval`
- Credit Card: `4532-1234-5678-9010`
- CVV: `847`
- Expiration: `03/27`

---

## CRITICAL VULNERABILITIES TO IMPLEMENT

### 1. Product Search (Primary Attack Vector)

**Vulnerable Code Pattern:**
```python
@bp.route('/products')
def products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    conn = sqlite3.connect('techhub_blueprint/techhub.db')
    cursor = conn.cursor()
    
    # VULNERABLE - Direct string concatenation
    if search:
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'"
    elif category:
        query = f"SELECT * FROM products WHERE category = '{category}'"
    else:
        query = "SELECT * FROM products"
    
    cursor.execute(query)  # NO PARAMETERIZATION
    products = cursor.fetchall()
    conn.close()
    
    return render_template('products.html', products=products)
```

**Exploit Examples Students Should Discover:**
- `' OR '1'='1` - Returns all products
- `' UNION SELECT null,null,null,null,null,null,null --` - Column enumeration
- `' UNION SELECT id, username, email, credit_card, cvv, expiration, null FROM customers --` - Data exfiltration

### 2. Login Form (Secondary Vulnerability)

**Vulnerable Code Pattern:**
```python
@bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('techhub_blueprint/techhub.db')
    cursor = conn.cursor()
    
    # VULNERABLE - Allows authentication bypass
    query = f"SELECT * FROM customers WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['customer_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('techhub.account'))
    
    return redirect(url_for('techhub.login'))
```

**Exploit Examples:**
- Username: `admin' --` (bypasses password check)
- Username: `' OR '1'='1' --` (logs in as first user)

### 3. Admin Login (Same Vulnerability)

```python
# Same pattern for admin authentication
query = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{password}'"
```

---

## EARLY 2000s STYLING REQUIREMENTS

### Visual Design Characteristics

**Color Scheme:**
- Primary: `#003366` (dark blue)
- Secondary: `#FF6600` (orange)
- Background: `#F0F0F0` (light gray)
- Headers: `#336699` (medium blue)
- Links: `#0066CC` (bright blue)
- Visited links: `#663399` (purple)

**Typography:**
- Font family: `Verdana, Arial, sans-serif`
- Font sizes: 10px, 11px, 12px, 14px (small by modern standards)
- Bold headers with `<font>` tag aesthetic (but use CSS)

**Layout Elements:**
- Fixed width: 980px centered
- Table-based visual structure (use CSS Grid/Flexbox to mimic tables)
- Heavy borders: 1px solid everywhere
- Beveled buttons with `border: outset 2px`
- Lots of horizontal rules `<hr>`
- Navigation bar with pipe separators: `Home | Products | Cart | Login`
- Footer with copyright and "Best viewed in Internet Explorer 6.0"

**UI Components:**
- Animated GIF "New!" badges
- Visitor counter aesthetic
- "Powered by" badges
- Drop shadows using `box-shadow: 3px 3px 5px #666`
- Gradient backgrounds (CSS gradients mimicking old GIF backgrounds)
- Star rating graphics (★★★★☆)
- "Add to Cart" buttons with shopping cart icons

**Product Display:**
- Grid layout with thick borders
- Small thumbnail images (200x200px max)
- Price in bold red or green
- "In Stock" / "Out of Stock" badges
- Specifications in bullet points

**Forms:**
- Thick input borders
- Required field asterisks (*)
- Submit buttons with 3D effect
- Fieldsets with legends
- Inline validation text in red

---

## FUNCTIONALITY REQUIREMENTS

### Public Routes

**Homepage (`/`)**
- Featured products carousel (static, no JavaScript slider)
- "Special Offers" section
- Category quick links
- Search bar (VULNERABLE)
- "Welcome to TechHub Electronics!" banner

**Products Page (`/products`)**
- Grid display of all products
- Category filter sidebar (VULNERABLE to SQLi)
- Search functionality (VULNERABLE)
- Sort options: Price Low-High, Price High-Low, Name A-Z
- Each product shows: image, name, price, "Add to Cart" button

**Product Detail (`/product/<id>`)**
- Large product image
- Full description
- Price
- Stock status
- Quantity selector
- "Add to Cart" button
- Breadcrumb navigation

**Shopping Cart (`/cart`)**
- Display cart items from session
- Quantity adjustment
- Remove item button
- Subtotal calculation
- "Proceed to Checkout" button
- "Continue Shopping" link

**Customer Registration (`/register`)**
- Username, password, email (required)
- Full name, address, city, state, zip
- Credit card, CVV, expiration (optional but encouraged)
- "Save payment info for faster checkout" checkbox
- Submit creates account in customers table

**Customer Login (`/login`)**
- Username and password form (VULNERABLE)
- "Forgot password?" link (non-functional)
- "New customer? Register here" link

**Checkout (`/checkout`)**
- Requires login
- Displays cart summary
- Uses stored payment info if available
- Otherwise requires manual entry
- Creates order in orders table
- Creates order_items entries
- Clears cart session
- Redirects to confirmation

**Order Confirmation (`/order/<id>`)**
- "Thank you for your order!"
- Order number
- Order summary
- Total
- "Expected delivery: 5-7 business days"

**Customer Account (`/account`)**
- Display account info
- Edit profile form (can update payment info)
- Link to order history

**Order History (`/orders`)**
- List all orders for logged-in customer
- Order date, total, status
- Click order to see details

### Admin Routes (all require admin login)

**Admin Login (`/admin/login`)**
- Separate from customer login
- Username and password (VULNERABLE to same SQLi)

**Admin Dashboard (`/admin`)**
- Total products count
- Total customers count
- Total orders count
- Recent orders list
- Quick links to management pages

**Product Management (`/admin/products`)**
- Table listing all products
- Edit and Delete buttons per product
- "Add New Product" button

**Add Product (`/admin/products/add`)**
- Form: name, description, price, category, stock
- Image upload to `/static/uploads/products/`
- Stores filename in database

**Edit Product (`/admin/products/edit/<id>`)**
- Pre-filled form with product data
- Can change image
- Update query (can be VULNERABLE if extending)

**Customer Management (`/admin/customers`)**
- Table listing all customers
- Shows username, email, full_name
- "View Details" button shows full record INCLUDING payment info
- Delete customer button

**Add Customer (`/admin/customers/add`)**
- Form with all customer fields
- Creates account without email verification

**Bulk Customer Upload (`/admin/customers/bulk`)**
- CSV upload form
- Expected format: `username,password,email,full_name,address,city,state,zip,credit_card,cvv,expiration`
- Parses CSV and inserts all rows
- Shows success message with count

---

## BLUEPRINT INITIALIZATION

### `__init__.py`

```python
from flask import Blueprint
import os
import sqlite3

bp = Blueprint('techhub', __name__, 
               template_folder='templates',
               static_folder='static',
               url_prefix='/techhub')

# Import routes after blueprint creation
from . import routes

def init_db():
    """Initialize database with schema and seed data"""
    db_path = os.path.join(os.path.dirname(__file__), 'techhub.db')
    
    # Only create if doesn't exist
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''CREATE TABLE products ...''')
        cursor.execute('''CREATE TABLE customers ...''')
        cursor.execute('''CREATE TABLE admins ...''')
        cursor.execute('''CREATE TABLE orders ...''')
        cursor.execute('''CREATE TABLE order_items ...''')
        
        # Insert seed data
        cursor.execute("INSERT INTO admins ...")
        cursor.execute("INSERT INTO products ...")
        cursor.execute("INSERT INTO customers ...")
        
        conn.commit()
        conn.close()

# Initialize database when blueprint is registered
init_db()
```

### Clean `app.py` for Testing

```python
from flask import Flask, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

# Configure upload folder
UPLOAD_FOLDER = 'techhub_blueprint/static/uploads/products'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Register blueprint
from techhub_blueprint import bp as techhub_bp
app.register_blueprint(techhub_bp)

@app.route('/')
def index():
    return redirect(url_for('techhub.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## SESSION MANAGEMENT

**Cart stored in session:**
```python
session['cart'] = {
    'product_id': {'name': 'Product Name', 'price': 99.99, 'quantity': 2}
}
```

**User authentication:**
```python
session['customer_id'] = user_id
session['username'] = username
```

**Admin authentication:**
```python
session['admin_id'] = admin_id
session['admin_username'] = username
```

---

## ADDITIONAL IMPLEMENTATION NOTES

1. **No input sanitization anywhere** - This is critical for the training exercise
2. **Use `sqlite3.connect()` directly in routes** - Don't use SQLAlchemy or other ORMs that auto-parameterize
3. **Store passwords in plain text** - Adds to the "bad security practices" theme
4. **Credit cards unencrypted** - Exactly as described in case study
5. **No HTTPS enforcement** - Period-appropriate
6. **Verbose error messages** - Display raw SQL errors to aid student learning
7. **No CSRF protection** - Another vulnerability to discover
8. **No rate limiting** - Allow unlimited SQLi attempts
9. **Console logging** - Log all executed SQL queries to terminal for educational visibility

---

## SUCCESS CRITERIA

Students should be able to:
1. Discover the search vulnerability through manual testing
2. Enumerate column count using UNION SELECT with nulls
3. Extract customer table data including payment information
4. Bypass login using `' --` or `' OR '1'='1' --`
5. Access admin panel without credentials
6. Understand why parameterized queries prevent these attacks

The application should feel authentically "old web" while being technically accurate to the Marcus Chen case study.