#!/usr/bin/env python3
"""
ETL Pipeline for Retail Supply Chain Optimizer.
Extracts data from CSV files, calculates KPIs, and loads into the database.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration (uses environment variables)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'retail_supply_chain'),
    'port': int(os.getenv('DB_PORT', 3306))
}

class ETLPipeline:
    """Main ETL Pipeline class"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.data_dir = "data"
        
    def connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info("✓ Database connection established")
            return True
        except Error as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
    
    def close_database(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("✓ Database connection closed")
    
    def load_csv(self, filename):
        """Load CSV file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            logger.info(f"✓ Loaded {filename} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"✗ Failed to load {filename}: {e}")
            return None
    
    def load_stores(self, df):
        """Load stores data into database"""
        try:
            for _, row in df.iterrows():
                sql = """
                    INSERT INTO stores (storeCode, storeName, city, state, country, storeType)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    storeName = VALUES(storeName), city = VALUES(city), state = VALUES(state)
                """
                self.cursor.execute(sql, (
                    row['storeCode'], row['storeName'], row['city'],
                    row['state'], row['country'], row['storeType']
                ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} stores")
        except Error as e:
            logger.error(f"✗ Error loading stores: {e}")
            self.connection.rollback()
    
    def load_products(self, df):
        """Load products data into database"""
        try:
            for _, row in df.iterrows():
                sql = """
                    INSERT INTO products (productCode, productName, category, subcategory, unitCost, unitPrice)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    productName = VALUES(productName), category = VALUES(category)
                """
                self.cursor.execute(sql, (
                    row['productCode'], row['productName'], row['category'],
                    row['subcategory'], row['unitCost'], row['unitPrice']
                ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} products")
        except Error as e:
            logger.error(f"✗ Error loading products: {e}")
            self.connection.rollback()
    
    def load_suppliers(self, df):
        """Load suppliers data into database"""
        try:
            for _, row in df.iterrows():
                sql = """
                    INSERT INTO suppliers (supplierCode, supplierName, country, leadTimeDays, qualityRating)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    supplierName = VALUES(supplierName), leadTimeDays = VALUES(leadTimeDays)
                """
                self.cursor.execute(sql, (
                    row['supplierCode'], row['supplierName'], row['country'],
                    row['leadTimeDays'], row['qualityRating']
                ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} suppliers")
        except Error as e:
            logger.error(f"✗ Error loading suppliers: {e}")
            self.connection.rollback()
    
    def load_inventory(self, df):
        """Load inventory data into database"""
        try:
            # Get store and product IDs
            self.cursor.execute("SELECT id, storeCode FROM stores")
            stores = {row['storeCode']: row['id'] for row in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT id, productCode FROM products")
            products = {row['productCode']: row['id'] for row in self.cursor.fetchall()}
            
            for _, row in df.iterrows():
                store_id = stores.get(row['storeCode'])
                product_id = products.get(row['productCode'])
                
                if store_id and product_id:
                    sql = """
                        INSERT INTO inventory (storeId, productId, quantityOnHand, reorderPoint, safetyStock, lastRestockDate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        quantityOnHand = VALUES(quantityOnHand), lastRestockDate = VALUES(lastRestockDate)
                    """
                    self.cursor.execute(sql, (
                        store_id, product_id, row['quantityOnHand'],
                        row['reorderPoint'], row['safetyStock'], row['lastRestockDate']
                    ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} inventory records")
        except Error as e:
            logger.error(f"✗ Error loading inventory: {e}")
            self.connection.rollback()
    
    def load_sales(self, df):
        """Load sales data into database"""
        try:
            # Get store and product IDs
            self.cursor.execute("SELECT id, storeCode FROM stores")
            stores = {row['storeCode']: row['id'] for row in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT id, productCode FROM products")
            products = {row['productCode']: row['id'] for row in self.cursor.fetchall()}
            
            for _, row in df.iterrows():
                store_id = stores.get(row['storeCode'])
                product_id = products.get(row['productCode'])
                
                if store_id and product_id:
                    sql = """
                        INSERT INTO sales (transactionId, storeId, productId, quantity, unitPrice, totalSales, costOfGoods, saleDate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(sql, (
                        row['transactionId'], store_id, product_id, row['quantity'],
                        row['unitPrice'], row['totalSales'], row['costOfGoods'], row['saleDate']
                    ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} sales transactions")
        except Error as e:
            logger.error(f"✗ Error loading sales: {e}")
            self.connection.rollback()
    
    def load_orders(self, df):
        """Load orders data into database"""
        try:
            # Get IDs
            self.cursor.execute("SELECT id, storeCode FROM stores")
            stores = {row['storeCode']: row['id'] for row in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT id, productCode FROM products")
            products = {row['productCode']: row['id'] for row in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT id, supplierCode FROM suppliers")
            suppliers = {row['supplierCode']: row['id'] for row in self.cursor.fetchall()}
            
            for _, row in df.iterrows():
                store_id = stores.get(row['storeCode'])
                product_id = products.get(row['productCode'])
                supplier_id = suppliers.get(row['supplierCode'])
                
                if store_id and product_id and supplier_id:
                    sql = """
                        INSERT INTO orders (orderId, storeId, productId, supplierId, quantity, orderDate, expectedDeliveryDate, actualDeliveryDate, orderStatus)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(sql, (
                        row['orderId'], store_id, product_id, supplier_id, row['quantity'],
                        row['orderDate'], row['expectedDeliveryDate'], 
                        row['actualDeliveryDate'] if pd.notna(row['actualDeliveryDate']) else None,
                        row['orderStatus']
                    ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} orders")
        except Error as e:
            logger.error(f"✗ Error loading orders: {e}")
            self.connection.rollback()
    
    def load_returns(self, df):
        """Load returns data into database"""
        try:
            # Get store and product IDs
            self.cursor.execute("SELECT id, storeCode FROM stores")
            stores = {row['storeCode']: row['id'] for row in self.cursor.fetchall()}
            
            self.cursor.execute("SELECT id, productCode FROM products")
            products = {row['productCode']: row['id'] for row in self.cursor.fetchall()}
            
            for _, row in df.iterrows():
                store_id = stores.get(row['storeCode'])
                product_id = products.get(row['productCode'])
                
                if store_id and product_id:
                    sql = """
                        INSERT INTO returns (returnId, storeId, productId, quantity, returnDate, reason, refundAmount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    self.cursor.execute(sql, (
                        row['returnId'], store_id, product_id, row['quantity'],
                        row['returnDate'], row['reason'], row['refundAmount']
                    ))
            self.connection.commit()
            logger.info(f"✓ Loaded {len(df)} returns")
        except Error as e:
            logger.error(f"✗ Error loading returns: {e}")
            self.connection.rollback()
    
    def calculate_kpis(self):
        """Calculate and store KPI metrics"""
        try:
            logger.info("Calculating KPIs...")
            
            # Get all stores
            self.cursor.execute("SELECT id FROM stores")
            stores = [row['id'] for row in self.cursor.fetchall()]
            
            # Calculate KPIs for each store and overall
            metric_date = datetime.now().date()
            
            for store_id in stores:
                # Inventory Turnover = COGS / Average Inventory
                self.cursor.execute("""
                    SELECT COALESCE(SUM(costOfGoods), 0) as total_cogs
                    FROM sales WHERE storeId = %s AND saleDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                cogs = self.cursor.fetchone()['total_cogs']
                
                self.cursor.execute("""
                    SELECT COALESCE(AVG(quantityOnHand * (SELECT unitCost FROM products WHERE id = inventory.productId)), 0) as avg_inventory
                    FROM inventory WHERE storeId = %s
                """, (store_id,))
                avg_inventory = self.cursor.fetchone()['avg_inventory']
                
                inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
                
                # Days of Inventory = (Average Inventory / COGS) * 365
                days_of_inventory = (avg_inventory / cogs * 365) if cogs > 0 else 0
                
                # Gross Profit Margin = (Revenue - COGS) / Revenue
                self.cursor.execute("""
                    SELECT COALESCE(SUM(totalSales), 0) as total_revenue
                    FROM sales WHERE storeId = %s AND saleDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                revenue = self.cursor.fetchone()['total_revenue']
                
                gross_profit_margin = ((revenue - cogs) / revenue * 100) if revenue > 0 else 0
                
                # Order Fill Rate = Delivered Orders / Total Orders
                self.cursor.execute("""
                    SELECT COUNT(*) as total_orders,
                           SUM(CASE WHEN orderStatus = 'delivered' THEN 1 ELSE 0 END) as delivered_orders
                    FROM orders WHERE storeId = %s AND orderDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                order_data = self.cursor.fetchone()
                total_orders = order_data['total_orders']
                delivered_orders = order_data['delivered_orders']
                order_fill_rate = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
                
                # Stockout Rate = Items with 0 quantity / Total items
                self.cursor.execute("""
                    SELECT COUNT(*) as total_items,
                           SUM(CASE WHEN quantityOnHand = 0 THEN 1 ELSE 0 END) as stockout_items
                    FROM inventory WHERE storeId = %s
                """, (store_id,))
                stock_data = self.cursor.fetchone()
                total_items = stock_data['total_items']
                stockout_items = stock_data['stockout_items']
                stockout_rate = (stockout_items / total_items * 100) if total_items > 0 else 0
                
                # On-Time Delivery Rate
                self.cursor.execute("""
                    SELECT COUNT(*) as total_delivered,
                           SUM(CASE WHEN actualDeliveryDate <= expectedDeliveryDate THEN 1 ELSE 0 END) as on_time
                    FROM orders WHERE storeId = %s AND orderStatus = 'delivered' AND orderDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                delivery_data = self.cursor.fetchone()
                total_delivered = delivery_data['total_delivered']
                on_time_deliveries = delivery_data['on_time']
                on_time_delivery_rate = (on_time_deliveries / total_delivered * 100) if total_delivered > 0 else 0
                
                # Return Rate = Returned Items / Total Sold Items
                self.cursor.execute("""
                    SELECT COALESCE(SUM(quantity), 0) as total_returned
                    FROM returns WHERE storeId = %s AND returnDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                returned_items = self.cursor.fetchone()['total_returned']
                
                self.cursor.execute("""
                    SELECT COALESCE(SUM(quantity), 0) as total_sold
                    FROM sales WHERE storeId = %s AND saleDate >= DATE_SUB(%s, INTERVAL 365 DAY)
                """, (store_id, metric_date))
                sold_items = self.cursor.fetchone()['total_sold']
                
                return_rate = (returned_items / sold_items * 100) if sold_items > 0 else 0
                
                # Insert KPI metrics
                sql = """
                    INSERT INTO kpiMetrics (storeId, metricDate, inventoryTurnover, daysOfInventory, grossProfitMargin,
                                           orderFillRate, stockoutRate, onTimeDeliveryRate, returnRate, totalRevenue, totalCost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    inventoryTurnover = VALUES(inventoryTurnover),
                    daysOfInventory = VALUES(daysOfInventory),
                    grossProfitMargin = VALUES(grossProfitMargin),
                    orderFillRate = VALUES(orderFillRate),
                    stockoutRate = VALUES(stockoutRate),
                    onTimeDeliveryRate = VALUES(onTimeDeliveryRate),
                    returnRate = VALUES(returnRate),
                    totalRevenue = VALUES(totalRevenue),
                    totalCost = VALUES(totalCost)
                """
                self.cursor.execute(sql, (
                    store_id, metric_date, inventory_turnover, days_of_inventory, gross_profit_margin,
                    order_fill_rate, stockout_rate, on_time_delivery_rate, return_rate, revenue, cogs
                ))
            
            # Calculate overall KPIs (NULL storeId)
            self.cursor.execute("SELECT COALESCE(SUM(costOfGoods), 0) as total_cogs FROM sales WHERE saleDate >= DATE_SUB(%s, INTERVAL 365 DAY)", (metric_date,))
            total_cogs = self.cursor.fetchone()['total_cogs']
            
            self.cursor.execute("SELECT COALESCE(SUM(totalSales), 0) as total_revenue FROM sales WHERE saleDate >= DATE_SUB(%s, INTERVAL 365 DAY)", (metric_date,))
            total_revenue = self.cursor.fetchone()['total_revenue']
            
            overall_margin = ((total_revenue - total_cogs) / total_revenue * 100) if total_revenue > 0 else 0
            
            sql = """
                INSERT INTO kpiMetrics (storeId, metricDate, grossProfitMargin, totalRevenue, totalCost)
                VALUES (NULL, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                grossProfitMargin = VALUES(grossProfitMargin),
                totalRevenue = VALUES(totalRevenue),
                totalCost = VALUES(totalCost)
            """
            self.cursor.execute(sql, (metric_date, overall_margin, total_revenue, total_cogs))
            
            self.connection.commit()
            logger.info("✓ KPIs calculated and stored")
        except Error as e:
            logger.error(f"✗ Error calculating KPIs: {e}")
            self.connection.rollback()
    
    def run(self):
        """Execute the complete ETL pipeline"""
        logger.info("=" * 60)
        logger.info("RETAIL SUPPLY CHAIN ETL PIPELINE")
        logger.info("=" * 60)
        
        if not self.connect_database():
            return False
        
        try:
            # Load master data
            stores_df = self.load_csv("stores.csv")
            if stores_df is not None:
                self.load_stores(stores_df)
            
            products_df = self.load_csv("products.csv")
            if products_df is not None:
                self.load_products(products_df)
            
            suppliers_df = self.load_csv("suppliers.csv")
            if suppliers_df is not None:
                self.load_suppliers(suppliers_df)
            
            # Load transactional data
            inventory_df = self.load_csv("inventory.csv")
            if inventory_df is not None:
                self.load_inventory(inventory_df)
            
            sales_df = self.load_csv("sales.csv")
            if sales_df is not None:
                self.load_sales(sales_df)
            
            orders_df = self.load_csv("orders.csv")
            if orders_df is not None:
                self.load_orders(orders_df)
            
            returns_df = self.load_csv("returns.csv")
            if returns_df is not None:
                self.load_returns(returns_df)
            
            # Calculate KPIs
            self.calculate_kpis()
            
            logger.info("=" * 60)
            logger.info("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return True
            
        finally:
            self.close_database()

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
