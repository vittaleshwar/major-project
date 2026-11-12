import csv
import json
import os
from datetime import datetime, timedelta
import random

def create_sample_files():
    """Create sample data files for the data lake (without Parquet)"""
    
    # Create sample directory
    sample_dir = "sample_data"
    os.makedirs(sample_dir, exist_ok=True)
    
    print("Creating sample data files for Data Lake project...")
    
    # 1. Sales Data (CSV) - Main file for analysis
    print("1. Creating sales_data.csv...")
    sales_data = []
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet', 'Phone', 'Headphones']
    regions = ['North', 'South', 'East', 'West']
    
    for i in range(1, 101):
        sale_date = datetime.now() - timedelta(days=random.randint(1, 30))
        sale_price = round(random.uniform(10, 2000), 2)
        quantity = random.randint(1, 5)
        sales_data.append({
            'sale_id': i,
            'customer_id': random.randint(1000, 1100),
            'product': random.choice(products),
            'quantity': quantity,
            'price': sale_price,
            'total_amount': round(quantity * sale_price, 2),
            'region': random.choice(regions),
            'sale_date': sale_date.strftime('%Y-%m-%d'),
            'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash'])
        })
    
    with open(f'{sample_dir}/sales_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['sale_id', 'customer_id', 'product', 'quantity', 'price', 
                     'total_amount', 'region', 'sale_date', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sales_data)
    
    # 2. Customer Data (JSON)
    print("2. Creating customers.json...")
    customers = []
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
    
    for i in range(1, 51):
        join_date = datetime.now() - timedelta(days=random.randint(1, 365))
        customers.append({
            'customer_id': 1000 + i,
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'email': f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@example.com",
            'phone': f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'state': random.choice(['CA', 'NY', 'TX', 'FL', 'IL']),
            'join_date': join_date.strftime('%Y-%m-%d'),
            'membership_tier': random.choice(['Basic', 'Silver', 'Gold', 'Platinum']),
            'total_spent': round(random.uniform(100, 10000), 2)
        })
    
    with open(f'{sample_dir}/customers.json', 'w') as jsonfile:
        json.dump(customers, jsonfile, indent=2)
    
    # 3. Website Logs (CSV)
    print("3. Creating website_logs.csv...")
    logs = []
    pages = ['/home', '/products', '/about', '/contact', '/cart', '/checkout']
    
    for i in range(1, 201):
        log_time = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        logs.append({
            'log_id': f"LOG{i:04d}",
            'user_id': random.randint(1000, 1050) if random.random() > 0.3 else None,
            'page_url': random.choice(pages),
            'timestamp': log_time.strftime('%Y-%m-%d %H:%M:%S'),
            'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            'country': random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'DE', 'FR']),
            'duration_seconds': random.randint(1, 300),
        })
    
    with open(f'{sample_dir}/website_logs.csv', 'w', newline='') as csvfile:
        fieldnames = ['log_id', 'user_id', 'page_url', 'timestamp',
                     'browser', 'country', 'duration_seconds']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)
    
    # 4. Product Catalog (JSON)
    print("4. Creating products.json...")
    products_data = []
    categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports', 'Toys']
    
    for i in range(1, 31):
        price = round(random.uniform(5, 2000), 2)
        products_data.append({
            'product_id': f"P{i:03d}",
            'name': f"Product {i}",
            'category': random.choice(categories),
            'price': price,
            'stock': random.randint(0, 1000),
            'rating': round(random.uniform(1, 5), 1),
        })
    
    with open(f'{sample_dir}/products.json', 'w') as jsonfile:
        json.dump(products_data, jsonfile, indent=2)
    
    # 5. Simple README
    print("5. Creating README.txt...")
    
    readme_content = """SAMPLE DATA FILES FOR DATA LAKE PROJECT

Files included:
1. sales_data.csv - 100 sales transactions
2. customers.json - 50 customer records
3. website_logs.csv - 200 website logs
4. products.json - 30 product records

HOW TO USE IN THE DATA LAKE PROJECT:
1. Login to the Data Lake System
2. Create an S3 bucket
3. Upload these files
4. Run Glue Crawler
5. Execute Athena queries

Sample Queries:
----------------
1. Total sales by region:
   SELECT region, SUM(total_amount) as total_sales 
   FROM sales_data 
   GROUP BY region

2. Top customers:
   SELECT customer_id, SUM(total_amount) as total_spent
   FROM sales_data 
   GROUP BY customer_id 
   ORDER BY total_spent DESC 
   LIMIT 10

3. Website traffic analysis:
   SELECT browser, COUNT(*) as visits
   FROM website_logs 
   GROUP BY browser

4. Product analysis:
   SELECT category, AVG(price) as avg_price
   FROM products 
   GROUP BY category
"""
    
    with open(f'{sample_dir}/README.txt', 'w') as readme_file:
        readme_file.write(readme_content)
    
    print(f"\n✅ All sample files created in '{sample_dir}/' directory!")
    print("\n📁 Files created:")
    for file in os.listdir(sample_dir):
        file_path = os.path.join(sample_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        print(f"  • {file} ({size_kb:.1f} KB)")
    
    print("\n🚀 Now you can:")
    print("1. Run Django: python manage.py runserver")
    print("2. Login at: http://127.0.0.1:8000/")
    print("3. Create S3 bucket")
    print("4. Upload these files")
    print("5. Run queries!")

if __name__ == "__main__":
    create_sample_files()