# E-Commerce Website

A full-featured e-commerce platform built with HTML, CSS, JavaScript, Python/Flask, and MySQL.

## Features

- User Authentication (Login/Signup)
- Product Browsing and Categories (Electronics, Clothing, Toys)
- Shopping Cart Management
- Order Processing
- Responsive Design
- Navigation Bar with Search Functionality

## Tech Stack

- Frontend: HTML5, CSS3, JavaScript
- Backend: Python/Flask
- Database: MySQL
- Authentication: Flask-Login

## Project Structure

```
e-commerce/
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # HTML templates
├── app.py                # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MySQL database:
   - Create a new database named 'ecommerce'
   - Update database credentials in config.py

4. Run the application:
   ```bash
   python app.py
   ```

## Database Schema

The MySQL database includes the following tables:
- users (id, username, email, password, created_at)
- products (id, name, description, price, category, stock, image_url)
- cart (id, user_id, product_id, quantity)
- orders (id, user_id, total_amount, status, created_at)
- order_items (id, order_id, product_id, quantity, price)

## License

MIT 