from functools import wraps
from flask import session, redirect, url_for, flash

def customer_login_required(f):
    """Decorator to require customer login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('techhub.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in as admin to access this page.', 'error')
            return redirect(url_for('techhub.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_total(cart):
    """Calculate cart total"""
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return round(total, 2)

def get_cart_count(cart):
    """Get total number of items in cart"""
    count = 0
    for item in cart.values():
        count += item['quantity']
    return count
