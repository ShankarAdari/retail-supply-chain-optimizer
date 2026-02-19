#!/usr/bin/env python3
"""
Generate realistic retail supply chain datasets for the optimizer.
Creates CSV files for stores, products, suppliers, inventory, sales, orders, and returns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_STORES = 45
NUM_PRODUCTS = 200
NUM_SUPPLIERS = 30
DAYS_OF_DATA = 365  # One year of historical data

# Store locations (US-based)
STORE_CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
    ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
    ("Indianapolis", "IN"), ("Austin", "TX"), ("Memphis", "TN"), ("Boston", "MA"),
    ("Nashville", "TN"), ("Baltimore", "MD"), ("Louisville", "KY"), ("Portland", "OR"),
    ("Las Vegas", "NV"), ("Milwaukee", "WI"), ("Albuquerque", "NM"), ("Tucson", "AZ"),
    ("Fresno", "CA"), ("Mesa", "AZ"), ("Sacramento", "CA"), ("Atlanta", "GA"),
    ("Kansas City", "MO"), ("Long Beach", "CA"), ("Etats-Unis", "CA"), ("Plano", "TX"),
    ("Arlington", "TX"), ("New Orleans", "LA"), ("Wichita", "KS"), ("Cleveland", "OH"),
    ("Corpus Christi", "TX"), ("Lexington", "KY"), ("Henderson", "NV"), ("Stockton", "CA"),
]

# Product categories
CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Beauty", "Toys", "Books", "Food"]
SUBCATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Tablets", "Accessories"],
    "Clothing": ["Men", "Women", "Kids", "Shoes"],
    "Home & Garden": ["Furniture", "Decor", "Kitchen", "Bedding"],
    "Sports": ["Equipment", "Apparel", "Footwear", "Accessories"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
    "Toys": ["Action Figures", "Building Sets", "Dolls", "Games"],
    "Books": ["Fiction", "Non-Fiction", "Educational", "Comics"],
    "Food": ["Snacks", "Beverages", "Dairy", "Frozen"],
}

# Supplier countries
SUPPLIER_COUNTRIES = ["USA", "China", "Vietnam", "India", "Mexico", "Thailand", "Indonesia", "Philippines"]

def generate_stores():
    """Generate store data"""
    stores = []
    for i in range(NUM_STORES):
        city, state = STORE_CITIES[i % len(STORE_CITIES)]
        stores.append({
            "storeCode": f"ST{i+1:04d}",
            "storeName": f"{city} Store #{i+1}",
            "city": city,
            "state": state,
            "country": "USA",
            "storeType": np.random.choice(["flagship", "standard", "outlet"], p=[0.2, 0.6, 0.2])
        })
    return pd.DataFrame(stores)

def generate_products():
    """Generate product data"""
    products = []
    product_id = 1
    for category in CATEGORIES:
        for subcategory in SUBCATEGORIES[category]:
            for j in range(25):  # 25 products per subcategory
                unit_cost = np.random.uniform(5, 500)
                unit_price = unit_cost * np.random.uniform(1.3, 2.5)
                products.append({
                    "productCode": f"PRD{product_id:05d}",
                    "productName": f"{category} - {subcategory} Product {j+1}",
                    "category": category,
                    "subcategory": subcategory,
                    "unitCost": round(unit_cost, 2),
                    "unitPrice": round(unit_price, 2)
                })
                product_id += 1
    return pd.DataFrame(products)

def generate_suppliers():
    """Generate supplier data"""
    suppliers = []
    for i in range(NUM_SUPPLIERS):
        suppliers.append({
            "supplierCode": f"SUP{i+1:04d}",
            "supplierName": f"Supplier {i+1}",
            "country": np.random.choice(SUPPLIER_COUNTRIES),
            "leadTimeDays": np.random.randint(7, 60),
            "qualityRating": round(np.random.uniform(0.7, 1.0), 2)
        })
    return pd.DataFrame(suppliers)

def generate_inventory(stores_df, products_df):
    """Generate current inventory levels"""
    inventory = []
    for _, store in stores_df.iterrows():
        for _, product in products_df.sample(n=min(100, len(products_df))).iterrows():
            inventory.append({
                "storeCode": store["storeCode"],
                "productCode": product["productCode"],
                "quantityOnHand": int(np.random.randint(0, 500)),
                "reorderPoint": int(np.random.randint(50, 200)),
                "safetyStock": int(np.random.randint(20, 100)),
                "lastRestockDate": (datetime.now() - timedelta(days=int(np.random.randint(0, 30)))).date()
            })
    return pd.DataFrame(inventory)

def generate_sales(stores_df, products_df):
    """Generate sales transactions for the past year"""
    sales = []
    base_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
    
    for day in range(DAYS_OF_DATA):
        current_date = base_date + timedelta(days=int(day))
        num_transactions = int(np.random.randint(50, 200))
        
        for _ in range(num_transactions):
            store = stores_df.sample(1).iloc[0]
            product = products_df.sample(1).iloc[0]
            quantity = np.random.randint(1, 10)
            
            sales.append({
                "transactionId": f"TXN{len(sales)+1:08d}",
                "storeCode": store["storeCode"],
                "productCode": product["productCode"],
                "quantity": quantity,
                "unitPrice": product["unitPrice"],
                "totalSales": round(quantity * product["unitPrice"], 2),
                "costOfGoods": round(quantity * product["unitCost"], 2),
                "saleDate": current_date.date()
            })
    
    return pd.DataFrame(sales)

def generate_orders(stores_df, products_df, suppliers_df):
    """Generate purchase orders"""
    orders = []
    base_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
    
    for i in range(500):
        order_date = base_date + timedelta(days=int(np.random.randint(0, DAYS_OF_DATA)))
        store = stores_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        supplier = suppliers_df.sample(1).iloc[0]
        
        quantity = np.random.randint(50, 500)
        expected_delivery = order_date + timedelta(days=int(supplier["leadTimeDays"]))
        
        # 80% of orders are delivered on time
        if np.random.random() < 0.8:
            actual_delivery = expected_delivery + timedelta(days=int(np.random.randint(-2, 2)))
            status = "delivered"
        else:
            actual_delivery = None
            status = np.random.choice(["pending", "shipped", "cancelled"], p=[0.3, 0.5, 0.2])
        
        orders.append({
            "orderId": f"ORD{i+1:08d}",
            "storeCode": store["storeCode"],
            "productCode": product["productCode"],
            "supplierCode": supplier["supplierCode"],
            "quantity": quantity,
            "orderDate": order_date.date(),
            "expectedDeliveryDate": expected_delivery.date(),
            "actualDeliveryDate": actual_delivery.date() if actual_delivery else None,
            "orderStatus": status
        })
    
    return pd.DataFrame(orders)

def generate_returns(stores_df, products_df):
    """Generate product returns"""
    returns = []
    base_date = datetime.now() - timedelta(days=DAYS_OF_DATA)
    
    for i in range(200):
        return_date = base_date + timedelta(days=int(np.random.randint(0, DAYS_OF_DATA)))
        store = stores_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        quantity = np.random.randint(1, 5)
        
        returns.append({
            "returnId": f"RET{i+1:08d}",
            "storeCode": store["storeCode"],
            "productCode": product["productCode"],
            "quantity": quantity,
            "returnDate": return_date.date(),
            "reason": np.random.choice(["Defective", "Wrong Item", "Changed Mind", "Damaged", "Not as Described"]),
            "refundAmount": round(quantity * product["unitPrice"], 2)
        })
    
    return pd.DataFrame(returns)

def main():
    """Generate all datasets"""
    print("Generating retail supply chain datasets...")
    
    # Generate base data
    stores_df = generate_stores()
    products_df = generate_products()
    suppliers_df = generate_suppliers()
    
    print(f"✓ Generated {len(stores_df)} stores")
    print(f"✓ Generated {len(products_df)} products")
    print(f"✓ Generated {len(suppliers_df)} suppliers")
    
    # Generate transactional data
    inventory_df = generate_inventory(stores_df, products_df)
    sales_df = generate_sales(stores_df, products_df)
    orders_df = generate_orders(stores_df, products_df, suppliers_df)
    returns_df = generate_returns(stores_df, products_df)
    
    print(f"✓ Generated {len(inventory_df)} inventory records")
    print(f"✓ Generated {len(sales_df)} sales transactions")
    print(f"✓ Generated {len(orders_df)} purchase orders")
    print(f"✓ Generated {len(returns_df)} returns")
    
    # Create data directory
    import os
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to CSV
    stores_df.to_csv(f"{data_dir}/stores.csv", index=False)
    products_df.to_csv(f"{data_dir}/products.csv", index=False)
    suppliers_df.to_csv(f"{data_dir}/suppliers.csv", index=False)
    inventory_df.to_csv(f"{data_dir}/inventory.csv", index=False)
    sales_df.to_csv(f"{data_dir}/sales.csv", index=False)
    orders_df.to_csv(f"{data_dir}/orders.csv", index=False)
    returns_df.to_csv(f"{data_dir}/returns.csv", index=False)
    
    print(f"\n✓ All datasets saved to '{data_dir}/' directory")
    print("Ready for ETL pipeline processing!")

if __name__ == "__main__":
    main()
