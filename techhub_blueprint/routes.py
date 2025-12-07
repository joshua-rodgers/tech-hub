from flask import render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
import os
from werkzeug.utils import secure_filename
import csv
from .models import get_db_path
from .utils import customer_login_required, admin_login_required, get_cart_total, get_cart_count
from . import bp

# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@bp.route('/')
def index():
    """Homepage with featured products"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products LIMIT 6")
    featured_products = cursor.fetchall()
    conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('index.html', products=featured_products, cart_count=cart_count)


@bp.route('/products')
def products():
    """Products page with VULNERABLE search and category filter"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', '')

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    try:
        # VULNERABLE - Direct string concatenation for SQL injection training
        if search:
            query = f"SELECT * FROM products WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'"
            print(f"[VULNERABLE SQL] {query}")  # Log for educational visibility
        elif category:
            query = f"SELECT * FROM products WHERE category = '{category}'"
            print(f"[VULNERABLE SQL] {query}")
        else:
            query = "SELECT * FROM products"

        # Apply sorting
        if sort == 'price_low':
            query += " ORDER BY price ASC"
        elif sort == 'price_high':
            query += " ORDER BY price DESC"
        elif sort == 'name':
            query += " ORDER BY name ASC"

        cursor.execute(query)  # NO PARAMETERIZATION - intentionally vulnerable
        products_list = cursor.fetchall()

    except sqlite3.Error as e:
        # Verbose error messages for educational purposes
        flash(f'Database Error: {str(e)}', 'error')
        products_list = []

    conn.close()

    # Get unique categories for filter
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('products.html',
                           products=products_list,
                           categories=categories,
                           current_search=search,
                           current_category=category,
                           current_sort=sort,
                           cart_count=cart_count)


@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('techhub.products'))

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('product_detail.html', product=product, cart_count=cart_count)


@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to cart"""
    quantity = int(request.form.get('quantity', 1))

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('techhub.products'))

    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    product_id_str = str(product_id)

    # Add or update cart item
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'id': product[0],
            'name': product[1],
            'price': product[3],
            'quantity': quantity,
            'image_url': product[5]
        }

    session['cart'] = cart
    flash(f'Added {product[1]} to cart!', 'success')

    return redirect(url_for('techhub.cart'))


@bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart = session.get('cart', {})
    total = get_cart_total(cart)
    cart_count = get_cart_count(cart)

    return render_template('cart.html', cart=cart, total=total, cart_count=cart_count)


@bp.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    """Update cart item quantity"""
    quantity = int(request.form.get('quantity', 1))

    if 'cart' in session and product_id in session['cart']:
        if quantity > 0:
            session['cart'][product_id]['quantity'] = quantity
        else:
            del session['cart'][product_id]

        session.modified = True

    return redirect(url_for('techhub.cart'))


@bp.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    """Remove item from cart"""
    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True
        flash('Item removed from cart', 'success')

    return redirect(url_for('techhub.cart'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # VULNERABLE - plain text storage
        email = request.form.get('email')
        full_name = request.form.get('full_name', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        zip_code = request.form.get('zip_code', '')
        credit_card = request.form.get('credit_card', '')
        cvv = request.form.get('cvv', '')
        expiration = request.form.get('expiration', '')

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''INSERT INTO customers
                   (username, password, email, full_name, address, city, state, zip_code,
                    credit_card, cvv, expiration)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, password, email, full_name, address, city, state, zip_code,
                 credit_card, cvv, expiration)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('techhub.login'))

        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')

        finally:
            conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)
    return render_template('register.html', cart_count=cart_count)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login with VULNERABLE SQL injection"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        try:
            # VULNERABLE - Allows authentication bypass via SQL injection
            query = f"SELECT * FROM customers WHERE username = '{username}' AND password = '{password}'"
            print(f"[VULNERABLE SQL] {query}")  # Log for educational visibility

            cursor.execute(query)  # NO PARAMETERIZATION - intentionally vulnerable
            user = cursor.fetchone()

            if user:
                session['customer_id'] = user[0]
                session['username'] = user[1]
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('techhub.account'))
            else:
                flash('Invalid credentials', 'error')

        except sqlite3.Error as e:
            # Verbose error messages for educational purposes
            flash(f'Database Error: {str(e)}', 'error')

        finally:
            conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)
    return render_template('login.html', cart_count=cart_count)


@bp.route('/logout')
def logout():
    """Customer logout"""
    session.pop('customer_id', None)
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('techhub.index'))


@bp.route('/account')
@customer_login_required
def account():
    """Customer account page"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (session['customer_id'],))
    customer = cursor.fetchone()
    conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('account.html', customer=customer, cart_count=cart_count)


@bp.route('/update_account', methods=['POST'])
@customer_login_required
def update_account():
    """Update customer account information"""
    full_name = request.form.get('full_name', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    zip_code = request.form.get('zip_code', '')
    credit_card = request.form.get('credit_card', '')
    cvv = request.form.get('cvv', '')
    expiration = request.form.get('expiration', '')

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE customers
           SET full_name = ?, email = ?, address = ?, city = ?, state = ?,
               zip_code = ?, credit_card = ?, cvv = ?, expiration = ?
           WHERE id = ?''',
        (full_name, email, address, city, state, zip_code, credit_card, cvv, expiration,
         session['customer_id'])
    )
    conn.commit()
    conn.close()

    flash('Account updated successfully!', 'success')
    return redirect(url_for('techhub.account'))


@bp.route('/checkout', methods=['GET', 'POST'])
@customer_login_required
def checkout():
    """Checkout page"""
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty', 'error')
        return redirect(url_for('techhub.products'))

    if request.method == 'POST':
        # Get customer info
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (session['customer_id'],))
        customer = cursor.fetchone()

        # Calculate total
        total = get_cart_total(cart)

        # Create order
        cursor.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            (session['customer_id'], total, 'pending')
        )
        order_id = cursor.lastrowid

        # Create order items
        for item in cart.values():
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, item['id'], item['quantity'], item['price'])
            )

        conn.commit()
        conn.close()

        # Clear cart
        session['cart'] = {}
        session.modified = True

        flash('Order placed successfully!', 'success')
        return redirect(url_for('techhub.order_confirmation', order_id=order_id))

    total = get_cart_total(cart)
    cart_count = get_cart_count(cart)

    # Get customer info for pre-filling
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (session['customer_id'],))
    customer = cursor.fetchone()
    conn.close()

    return render_template('checkout.html', cart=cart, total=total, customer=customer, cart_count=cart_count)


@bp.route('/order/<int:order_id>')
@customer_login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Get order
    cursor.execute("SELECT * FROM orders WHERE id = ? AND customer_id = ?",
                   (order_id, session['customer_id']))
    order = cursor.fetchone()

    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('techhub.index'))

    # Get order items with product details
    cursor.execute('''
        SELECT oi.*, p.name, p.image_url
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,))
    order_items = cursor.fetchall()

    conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('order_confirmation.html', order=order, order_items=order_items, cart_count=cart_count)


@bp.route('/orders')
@customer_login_required
def order_history():
    """Order history page"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC",
                   (session['customer_id'],))
    orders = cursor.fetchall()
    conn.close()

    cart = session.get('cart', {})
    cart_count = get_cart_count(cart)

    return render_template('order_history.html', orders=orders, cart_count=cart_count)


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with VULNERABLE SQL injection"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        try:
            # VULNERABLE - Same SQL injection vulnerability as customer login
            query = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{password}'"
            print(f"[VULNERABLE SQL] {query}")  # Log for educational visibility

            cursor.execute(query)  # NO PARAMETERIZATION - intentionally vulnerable
            admin = cursor.fetchone()

            if admin:
                session['admin_id'] = admin[0]
                session['admin_username'] = admin[1]
                flash(f'Welcome, {admin[1]}!', 'success')
                return redirect(url_for('techhub.admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'error')

        except sqlite3.Error as e:
            # Verbose error messages for educational purposes
            flash(f'Database Error: {str(e)}', 'error')

        finally:
            conn.close()

    return render_template('admin/admin_base.html', page='login')


@bp.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('techhub.admin_login'))


@bp.route('/admin')
@admin_login_required
def admin_dashboard():
    """Admin dashboard"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM customers")
    customers_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    orders_count = cursor.fetchone()[0]

    # Get recent orders
    cursor.execute('''
        SELECT o.*, c.username
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.order_date DESC
        LIMIT 10
    ''')
    recent_orders = cursor.fetchall()

    conn.close()

    return render_template('admin/dashboard.html',
                           products_count=products_count,
                           customers_count=customers_count,
                           orders_count=orders_count,
                           recent_orders=recent_orders)


@bp.route('/admin/products')
@admin_login_required
def admin_products():
    """Admin product management"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    conn.close()

    return render_template('admin/products.html', products=products)


@bp.route('/admin/products/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        stock = int(request.form.get('stock'))

        # Handle image upload
        image_url = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = filename

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, description, price, category, image_url, stock) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, price, category, image_url, stock)
        )
        conn.commit()
        conn.close()

        flash('Product added successfully!', 'success')
        return redirect(url_for('techhub.admin_products'))

    return render_template('admin/add_product.html')


@bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_login_required
def admin_edit_product(product_id):
    """Edit product"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        stock = int(request.form.get('stock'))

        # Handle image upload
        cursor.execute("SELECT image_url FROM products WHERE id = ?", (product_id,))
        current_image = cursor.fetchone()[0]
        image_url = current_image

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = filename

        cursor.execute(
            '''UPDATE products
               SET name = ?, description = ?, price = ?, category = ?, image_url = ?, stock = ?
               WHERE id = ?''',
            (name, description, price, category, image_url, stock, product_id)
        )
        conn.commit()
        conn.close()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('techhub.admin_products'))

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    return render_template('admin/edit_product.html', product=product)


@bp.route('/admin/products/delete/<int:product_id>')
@admin_login_required
def admin_delete_product(product_id):
    """Delete product"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('techhub.admin_products'))


@bp.route('/admin/customers')
@admin_login_required
def admin_customers():
    """Admin customer management"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY username")
    customers = cursor.fetchall()
    conn.close()

    return render_template('admin/customers.html', customers=customers)


@bp.route('/admin/customers/add', methods=['GET', 'POST'])
@admin_login_required
def admin_add_customer():
    """Add new customer"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        zip_code = request.form.get('zip_code', '')
        credit_card = request.form.get('credit_card', '')
        cvv = request.form.get('cvv', '')
        expiration = request.form.get('expiration', '')

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''INSERT INTO customers
                   (username, password, email, full_name, address, city, state, zip_code,
                    credit_card, cvv, expiration)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, password, email, full_name, address, city, state, zip_code,
                 credit_card, cvv, expiration)
            )
            conn.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('techhub.admin_customers'))

        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')

        finally:
            conn.close()

    return render_template('admin/add_customer.html')


@bp.route('/admin/customers/delete/<int:customer_id>')
@admin_login_required
def admin_delete_customer(customer_id):
    """Delete customer"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('techhub.admin_customers'))


@bp.route('/admin/customers/bulk', methods=['GET', 'POST'])
@admin_login_required
def admin_bulk_upload():
    """Bulk customer upload via CSV"""
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('techhub.admin_bulk_upload'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('techhub.admin_bulk_upload'))

        if file:
            # Read CSV
            stream = file.stream.read().decode("UTF8")
            csv_reader = csv.reader(stream.splitlines())

            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()

            count = 0
            for row in csv_reader:
                if len(row) >= 11:  # Ensure all fields present
                    try:
                        cursor.execute(
                            '''INSERT INTO customers
                               (username, password, email, full_name, address, city, state,
                                zip_code, credit_card, cvv, expiration)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            row[:11]
                        )
                        count += 1
                    except sqlite3.IntegrityError:
                        continue  # Skip duplicates

            conn.commit()
            conn.close()

            flash(f'Successfully uploaded {count} customers!', 'success')
            return redirect(url_for('techhub.admin_customers'))

    return render_template('admin/bulk_upload.html')
