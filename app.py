from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from functools import wraps
from flask_mail import Message, Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Arsh%405354@localhost/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'  # Change this to your actual email

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail = Mail(app)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200))

class CartItem(db.Model):
    __tablename__ = 'cart_items'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    __tablename__ = 'orders'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address = db.Column(db.String(200), nullable=False)
    tracking_number = db.Column(db.String(50), unique=True)
    estimated_delivery = db.Column(db.DateTime)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    tracking_updates = db.relationship('OrderTracking', backref='order', lazy=True)
    cancellation_reason = db.Column(db.String(200))
    cancelled_at = db.Column(db.DateTime)

class OrderItem(db.Model):
    __tablename__ = 'order_items'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product')

class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to initialize database
def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create default admin user
        admin = User(
            username='admin',
            email='admin@ecommerce.com',
            password_hash=generate_password_hash('Admin@123'),
            is_admin=True
        )
        db.session.add(admin)
        
        # Add sample products
        sample_products = [
            Product(
                name='Smartphone X',
                description='Latest smartphone with amazing features',
                price=699.99,
                category='electronics',
                stock=50,
                image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            ),
            Product(
                name='Laptop Pro',
                description='Powerful laptop for professionals',
                price=1299.99,
                category='electronics',
                stock=30,
                image_url='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            ),
            Product(
                name='Cotton T-Shirt',
                description='Comfortable cotton t-shirt',
                price=19.99,
                category='clothing',
                stock=100,
                image_url='https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            ),
            Product(
                name='Denim Jeans',
                description='Classic blue denim jeans',
                price=49.99,
                category='clothing',
                stock=75,
                image_url='https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            ),
            Product(
                name='Remote Control Car',
                description='Fast RC car for kids',
                price=29.99,
                category='toys',
                stock=40,
                image_url='https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            ),
            Product(
                name='Building Blocks',
                description='Creative building blocks set',
                price=24.99,
                category='toys',
                stock=60,
                image_url='https://images.unsplash.com/photo-1587654780291-39c9404d746b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80'
            )
        ]
        
        for product in sample_products:
            db.session.add(product)
        
        db.session.commit()

# Routes
@app.route('/')
def home():
    category = request.args.get('category')
    search_query = request.args.get('search')
    
    query = Product.query
    
    if category:
        query = query.filter_by(category=category)
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    products = query.all()
    return render_template('index.html', products=products, current_category=category)

@app.route('/category/<category>')
def category(category):
    products = Product.query.filter_by(category=category).all()
    return render_template('index.html', products=products, current_category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password')
        # If the request is from modal, redirect back to home
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid email or password'}), 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            # If the request is from modal, redirect back to home
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Email already registered'}), 400
            return redirect(url_for('signup'))
        
        # Create first user as admin
        is_admin = User.query.count() == 0
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        
        # If the request is from modal, return success response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Registration successful'})
            
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        flash('You do not have permission to remove this item.')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.')
    return redirect(url_for('cart'))

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.')
        return redirect(url_for('orders'))
    return render_template('order_details.html', order=order)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            flash('Your cart is empty')
            return redirect(url_for('cart'))
        
        # Get shipping address from form
        shipping_address = f"{request.form.get('address')}, {request.form.get('city')}, {request.form.get('state')} {request.form.get('zip')}"
        
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Generate tracking number (you might want to use a more sophisticated method)
        tracking_number = f"TRK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate estimated delivery (3-5 business days from now)
        estimated_delivery = datetime.utcnow() + timedelta(days=5)
        
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            tracking_number=tracking_number,
            estimated_delivery=estimated_delivery
        )
        db.session.add(order)
        
        # Add initial tracking update
        tracking = OrderTracking(
            order=order,
            status='Order Placed',
            location='Warehouse',
            description='Your order has been received and is being processed.'
        )
        db.session.add(tracking)
        
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flash('Order placed successfully!')
        return redirect(url_for('order_details', order_id=order.id))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('checkout.html', cart_items=cart_items)

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id:
        flash('You are not authorized to cancel this order.', 'danger')
        return redirect(url_for('orders'))
    
    # Check if the order can be cancelled
    if order.status in ['delivered', 'cancelled']:
        flash('This order cannot be cancelled.', 'danger')
        return redirect(url_for('order_details', order_id=order_id))
    
    try:
        # Get the cancellation reason from the request
        data = request.get_json()
        reason = data.get('reason', 'No reason provided')
        
        # Update order status
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.cancelled_at = datetime.utcnow()
        
        # Add tracking update
        tracking_update = OrderTracking(
            order_id=order.id,
            status='cancelled',
            description=f'Order cancelled by customer. Reason: {reason}',
            timestamp=datetime.utcnow()
        )
        db.session.add(tracking_update)
        
        # Restore product stock
        for item in order.items:
            product = item.product
            product.stock += item.quantity
        
        db.session.commit()
        
        # Send email notification
        send_order_cancellation_email(order)
        
        flash('Order has been cancelled successfully.', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the order.', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 500

def send_order_cancellation_email(order):
    msg = Message(
        'Order Cancellation Confirmation',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[order.user.email]
    )
    
    msg.body = f'''Dear {order.user.name},

Your order #{order.id} has been cancelled.

Order Details:
- Order Date: {order.created_at.strftime('%B %d, %Y %I:%M %p')}
- Total Amount: ${order.total_amount:.2f}
- Cancellation Reason: {order.cancellation_reason}

If you did not request this cancellation, please contact our customer support immediately.

Thank you for your understanding.

Best regards,
Your Store Team
'''
    
    mail.send(msg)

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_orders=total_orders,
                         total_products=total_products,
                         recent_orders=recent_orders)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_details(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return render_template('admin/user_details.html', user=user, orders=orders)

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>')
@login_required
@admin_required
def admin_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

@app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        tracking = OrderTracking(
            order=order,
            status=new_status.title(),
            location=request.form.get('location', ''),
            description=request.form.get('description', f'Order status updated to {new_status}')
        )
        db.session.add(tracking)
        db.session.commit()
        flash('Order status updated successfully')
    return redirect(url_for('admin_order_details', order_id=order_id))

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        stock = int(request.form.get('stock'))
        
        # Handle image upload
        image_url = 'https://via.placeholder.com/200'  # Default image
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f"/static/uploads/{filename}"
        
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock,
            image_url=image_url
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.category = request.form.get('category')
        product.stock = int(request.form.get('stock'))
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_url = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        # Delete associated cart items first
        CartItem.query.filter_by(product_id=product_id).delete()
        
        # Delete associated order items
        OrderItem.query.filter_by(product_id=product_id).delete()
        
        # Delete the product
        db.session.delete(product)
        db.session.commit()
        
        flash('Product deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting product. Please try again.', 'error')
        print(f"Error deleting product: {str(e)}")
    
    return redirect(url_for('admin_products'))

@app.route('/admin/order/<int:order_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Delete associated order items first
        OrderItem.query.filter_by(order_id=order_id).delete()
        
        # Delete associated tracking updates
        OrderTracking.query.filter_by(order_id=order_id).delete()
        
        # Delete the order
        db.session.delete(order)
        db.session.commit()
        
        flash('Order deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting order. Please try again.', 'error')
        print(f"Error deleting order: {str(e)}")
    
    return redirect(url_for('admin_orders'))

if __name__ == '__main__':
    # Initialize the database with sample data
    init_db()
    app.run(debug=True) 