# E-Commerce Web Application

A beginner-friendly full-stack e-commerce web application built with **Python Django**. Users can browse products, add items to cart, and place orders.

## Features

- **User Authentication**: Sign up, login, and logout
- **Product Browsing**: Homepage with product grid and product detail pages
- **Shopping Cart**: Add/remove items, view cart summary
- **Checkout**: Place orders (requires login)
- **Admin Panel**: Manage products via Django admin
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **Backend**: Django 4.x, Python 3.x
- **Database**: SQLite (included, no setup needed)
- **Frontend**: HTML, CSS, JavaScript
- **Templates**: Django template engine

## Project Structure

```
├── ecommerce_project/     # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── store/                 # Main app (products, cart, orders)
│   ├── models.py         # Product, Cart, Order models
│   ├── views.py          # Request handlers
│   └── ...
├── templates/             # HTML templates
│   ├── base.html
│   └── store/
├── static/                # CSS, JS, images
│   └── css/
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Create a Virtual Environment (recommended)

```bash
python -m venv venv
```

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

Create the database tables:

```bash
python manage.py migrate
```

### 4. Create a Superuser (for admin panel)

```bash
python manage.py createsuperuser
```

Enter a username, email, and password when prompted.

### 5. Load Sample Products

```bash
python manage.py create_sample_products
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open your browser and go to: **http://127.0.0.1:8000/**

## Usage

1. **Browse Products**: Visit the homepage to see all products
2. **View Details**: Click a product to see its description and price
3. **Add to Cart**: Click "Add to Cart" on any product
4. **View Cart**: Click "Cart" in the navbar to see your items
5. **Checkout**: Log in, then click "Checkout" to place an order
6. **Admin**: Go to http://127.0.0.1:8000/admin/ to manage products (use superuser account)

## Admin Panel

- URL: `/admin/`
- Add, edit, and delete products
- View orders and order details
- Use the superuser account created in step 4

## Notes for Beginners

- Models are defined in `store/models.py`
- Views handle HTTP requests in `store/views.py`
- URLs map paths to views in `store/urls.py`
- Templates use Django's template language (variables, loops, etc.)
- Static files (CSS) are in the `static/` folder

## License

MIT - Feel free to use this project for learning!
