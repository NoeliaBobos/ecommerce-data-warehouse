import csv
import os
import random
from datetime import datetime, timedelta

# -----------------------------
# PATH CONFIGURATION
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SOURCE_RAW_PATH = os.path.join(BASE_DIR, "data", "source_raw")

# -----------------------------
# DATA VOLUME CONFIGURATION
# -----------------------------

NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 500
NUM_ORDERS = 20000

# -----------------------------
# FIXED REFERENCE DATA
# -----------------------------

CATEGORIES = [
    [1, "Electronics"],
    [2, "Home"],
    [3, "Fashion"],
    [4, "Books"],
    [5, "Sports"],
    [6, "Beauty"]
]

STORES = [
    [1, "TechStore Oradea", "Oradea"],
    [2, "CityMall Cluj", "Cluj-Napoca"],
    [3, "Market Hub Bucuresti", "Bucuresti"],
    [4, "Retail Point Timisoara", "Timisoara"],
    [5, "Shop Center Iasi", "Iasi"]
]

CUSTOMER_CITIES = [
    "Oradea",
    "Cluj-Napoca",
    "Bucuresti",
    "Timisoara",
    "Iasi",
    "Constanta",
    "Brasov",
    "Sibiu",
    "Craiova",
    "Arad"
]

FIRST_NAMES = [
    "Andrei", "Maria", "Ion", "Elena", "Mihai", "Ioana", "Alexandru", "Gabriela",
    "Daniel", "Ana", "Cristian", "Bianca", "Stefan", "Diana", "Vlad", "Larisa",
    "Radu", "Irina", "George", "Adina", "Paul", "Denisa", "Robert", "Teodora",
    "Florin", "Raluca", "Cosmin", "Alina", "David", "Monica"
]

LAST_NAMES = [
    "Popescu", "Ionescu", "Georgescu", "Dumitrescu", "Stan", "Radu", "Marin",
    "Gheorghe", "Dobre", "Constantin", "Stoica", "Munteanu", "Ilie", "Tudor",
    "Petrescu", "Neagu", "Barbu", "Florea", "Nistor", "Enache"
]

PRODUCT_NAMES = {
    1: ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard", "Mouse", "Headphones", "Smartwatch", "Printer", "Speaker"],
    2: ["Chair", "Desk", "Lamp", "Pillow", "Blanket", "Curtains", "Plate Set", "Cookware Set", "Storage Box", "Wall Clock"],
    3: ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Dress", "Shirt", "Sweater", "Backpack", "Hat", "Scarf"],
    4: ["Novel", "Notebook", "Dictionary", "Atlas", "Cookbook", "Biography", "Textbook", "Planner", "Album", "Guide"],
    5: ["Football", "Basketball", "Tennis Racket", "Yoga Mat", "Dumbbell", "Bicycle Helmet", "Water Bottle", "Running Shoes", "Fitness Band", "Sports Bag"],
    6: ["Shampoo", "Perfume", "Face Cream", "Body Lotion", "Lipstick", "Mascara", "Soap", "Conditioner", "Hair Dryer", "Nail Polish"]
}

PRICE_RANGES = {
    1: (100, 5000),
    2: (30, 1500),
    3: (40, 800),
    4: (20, 300),
    5: (25, 2000),
    6: (15, 600)
}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def write_csv(file_path, header, rows):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)

def random_date(start_date, end_date):
    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    return start_date + timedelta(days=random_days)

def random_signup_date(start_date, end_date):
    return random_date(start_date, end_date).strftime("%Y-%m-%d")

def weighted_order_status():
    value = random.random()
    if value < 0.85:
        return "Completed"
    elif value < 0.95:
        return "Pending"
    return "Cancelled"

def get_discount():
    value = random.random()
    if value < 0.70:
        return 0.00
    elif value < 0.85:
        return 0.05
    elif value < 0.95:
        return 0.10
    return 0.15

def apply_price_variation(base_price):
    variation_percent = random.uniform(-0.05, 0.05)
    varied_price = base_price * (1 + variation_percent)
    return round(varied_price, 2)

def build_product_price_lookup(products):
    price_lookup = {}
    for product in products:
        product_id = product[0]
        price = product[3]
        price_lookup[product_id] = price
    return price_lookup

# -----------------------------
# GENERATE FIXED TABLES
# -----------------------------

def generate_categories():
    file_path = os.path.join(SOURCE_RAW_PATH, "categories.csv")
    header = ["category_id", "category_name"]
    write_csv(file_path, header, CATEGORIES)
    print("categories.csv generated successfully.")

def generate_stores():
    file_path = os.path.join(SOURCE_RAW_PATH, "stores.csv")
    header = ["store_id", "store_name", "city"]
    write_csv(file_path, header, STORES)
    print("stores.csv generated successfully.")

# -----------------------------
# GENERATE CUSTOMERS
# -----------------------------

def generate_customers():
    customers = []
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)

    for customer_id in range(1, NUM_CUSTOMERS + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        city = random.choice(CUSTOMER_CITIES)
        signup_date = random_signup_date(start_date, end_date)
        email = f"{first_name.lower()}.{last_name.lower()}{customer_id}@example.com"

        customers.append([
            customer_id,
            first_name,
            last_name,
            email,
            city,
            signup_date
        ])

    file_path = os.path.join(SOURCE_RAW_PATH, "customers.csv")
    header = ["customer_id", "first_name", "last_name", "email", "city", "signup_date"]
    write_csv(file_path, header, customers)
    print("customers.csv generated successfully.")

# -----------------------------
# GENERATE PRODUCTS
# -----------------------------

def generate_products():
    products = []

    for product_id in range(1, NUM_PRODUCTS + 1):
        category_id = random.randint(1, 6)
        base_name = random.choice(PRODUCT_NAMES[category_id])
        product_name = f"{base_name} Model {product_id}"
        min_price, max_price = PRICE_RANGES[category_id]
        price = round(random.uniform(min_price, max_price), 2)

        products.append([
            product_id,
            product_name,
            category_id,
            price
        ])

    file_path = os.path.join(SOURCE_RAW_PATH, "products.csv")
    header = ["product_id", "product_name", "category_id", "price"]
    write_csv(file_path, header, products)
    print("products.csv generated successfully.")

    return products

# -----------------------------
# GENERATE ORDERS
# -----------------------------

def generate_orders():
    orders = []
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)

    for order_id in range(1, NUM_ORDERS + 1):
        customer_id = random.randint(1, NUM_CUSTOMERS)
        store_id = random.randint(1, len(STORES))
        order_date = random_date(start_date, end_date).strftime("%Y-%m-%d")
        status = weighted_order_status()

        orders.append([
            order_id,
            customer_id,
            store_id,
            order_date,
            status
        ])

    file_path = os.path.join(SOURCE_RAW_PATH, "orders.csv")
    header = ["order_id", "customer_id", "store_id", "order_date", "status"]
    write_csv(file_path, header, orders)
    print("orders.csv generated successfully.")

# -----------------------------
# GENERATE ORDER ITEMS
# -----------------------------

def generate_order_items(product_price_lookup):
    order_items = []
    order_item_id = 1

    for order_id in range(1, NUM_ORDERS + 1):
        num_items = random.randint(1, 5)
        used_products = random.sample(range(1, NUM_PRODUCTS + 1), num_items)

        for product_id in used_products:
            quantity = random.randint(1, 4)
            base_price = product_price_lookup[product_id]
            unit_price = apply_price_variation(base_price)
            discount = get_discount()

            order_items.append([
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                discount
            ])

            order_item_id += 1

    file_path = os.path.join(SOURCE_RAW_PATH, "order_items.csv")
    header = ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount"]
    write_csv(file_path, header, order_items)
    print("order_items.csv generated successfully.")

# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    generate_categories()
    generate_stores()
    generate_customers()
    products = generate_products()
    generate_orders()

    product_price_lookup = build_product_price_lookup(products)
    generate_order_items(product_price_lookup)

    print("All source files generated successfully.")