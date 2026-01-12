"""
Data Transformation Module
Handles data cleaning, enrichment, and business logic
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple
from .config import Config, logger


class DataTransformer:
    """Handles ETL transformation logic"""
    
    def __init__(self):
        """Initialize transformer"""
        self.config = Config()
    
    def clean_data(self, df: pd.DataFrame, collection_name: str) -> pd.DataFrame:
        """Clean and standardize data"""
        logger.info(f"Cleaning data for {collection_name}")
        df = df.drop_duplicates()
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col not in ['_id', 'email']:
                df[col] = df[col].astype(str).str.strip()
        return df
    
    def normalize_dates(self, df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """Normalize date fields"""
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    
    def create_date_dimension(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create date dimension table"""
        logger.info("Creating date dimension...")
        all_dates = []
        
        if 'orders' in data:
            df = data['orders']
            for col in ['orderDate', 'createdAt', 'created_at']:
                if col in df.columns:
                    all_dates.extend(pd.to_datetime(df[col], errors='coerce').dropna())
        
        if 'payments' in data:
            df = data['payments']
            for col in ['paymentDate', 'payment_date', 'createdAt']:
                if col in df.columns:
                    all_dates.extend(pd.to_datetime(df[col], errors='coerce').dropna())
        
        if not all_dates:
            unique_dates = pd.date_range(start='2020-01-01', end='2026-12-31', freq='D')
        else:
            unique_dates = pd.Series(all_dates).dt.normalize().drop_duplicates().sort_values()
        
        dim_date = pd.DataFrame({'date': unique_dates})
        dim_date['date_id'] = (dim_date['date'].dt.year * 10000 + 
                                dim_date['date'].dt.month * 100 + 
                                dim_date['date'].dt.day).astype(int)
        dim_date['year'] = dim_date['date'].dt.year
        dim_date['quarter'] = dim_date['date'].dt.quarter
        dim_date['month'] = dim_date['date'].dt.month
        dim_date['month_name'] = dim_date['date'].dt.month_name()
        dim_date['day'] = dim_date['date'].dt.day
        dim_date['day_of_week'] = dim_date['date'].dt.dayofweek
        dim_date['day_name'] = dim_date['date'].dt.day_name()
        dim_date['week_of_year'] = dim_date['date'].dt.isocalendar().week
        dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
        
        dim_date = dim_date.drop_duplicates(subset=['date_id'])
        logger.info(f"  Created date dimension with {len(dim_date)} dates")
        return dim_date
    
    def create_product_dimension(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create product dimension table using business IDs"""
        logger.info("Creating product dimension...")
        products = data['products'].copy()
        categories = data.get('categories', pd.DataFrame())
        
        id_col = 'productId' if 'productId' in products.columns else '_id'
        
        if not categories.empty and 'categoryId' in products.columns:
            products = products.merge(categories[['categoryId', 'categoryName']], on='categoryId', how='left')
        
        dim_product = pd.DataFrame()
        dim_product['product_id'] = products[id_col].astype(str)
        dim_product['product_name'] = products['productName'] if 'productName' in products.columns else (products['name'] if 'name' in products.columns else 'Unknown')
        dim_product['category_name'] = products['categoryName'] if 'categoryName' in products.columns else 'Uncategorized'
        
        if 'unitPrice' in products.columns:
            dim_product['price'] = pd.to_numeric(products['unitPrice'], errors='coerce').fillna(0)
        else:
            dim_product['price'] = pd.to_numeric(products.get('price', 0), errors='coerce').fillna(0) if isinstance(products.get('price'), pd.Series) else products.get('price', 0)
            
        if 'unitCost' in products.columns:
            dim_product['cost'] = pd.to_numeric(products['unitCost'], errors='coerce').fillna(0)
        else:
            dim_product['cost'] = pd.to_numeric(products.get('cost', 0), errors='coerce').fillna(0) if isinstance(products.get('cost'), pd.Series) else products.get('cost', 0)
            
        dim_product['brand'] = products['brand'] if 'brand' in products.columns else 'Generic'
        dim_product['description'] = products['description'] if 'description' in products.columns else ''
        dim_product['created_at'] = pd.to_datetime(products.get('createdAt', datetime.now()), errors='coerce')
        dim_product['updated_at'] = pd.to_datetime(products.get('updatedAt', datetime.now()), errors='coerce')
        
        dim_product = dim_product.drop_duplicates(subset=['product_id'])
        logger.info(f"  Created product dimension with {len(dim_product)} products")
        return dim_product
    
    def create_customer_dimension(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create customer dimension table using business IDs"""
        logger.info("Creating customer dimension...")
        users = data['users'].copy()
        
        id_col = 'userId' if 'userId' in users.columns else '_id'
        
        if 'firstName' in users.columns and 'lastName' in users.columns:
            users['full_name'] = users['firstName'] + " " + users['lastName']
        else:
            users['full_name'] = users['fullName'] if 'fullName' in users.columns else users.get('name', 'Unknown')
            
        dim_customer = pd.DataFrame()
        dim_customer['customer_id'] = users[id_col].astype(str)
        dim_customer['full_name'] = users['full_name']
        dim_customer['email'] = users['email'] if 'email' in users.columns else ''
        dim_customer['gender'] = users['gender'] if 'gender' in users.columns else 'Unknown'
        dim_customer['registration_date'] = pd.to_datetime(users.get('registrationDate', users.get('createdAt')), errors='coerce')
        dim_customer['customer_segment'] = users['role'] if 'role' in users.columns else 'Customer'
        dim_customer['created_at'] = pd.to_datetime(users.get('createdAt', datetime.now()), errors='coerce')
        dim_customer['updated_at'] = pd.to_datetime(users.get('updatedAt', datetime.now()), errors='coerce')
        
        dim_customer = dim_customer.drop_duplicates(subset=['customer_id'])
        logger.info(f"  Created customer dimension with {len(dim_customer)} customers")
        return dim_customer
    
    def create_region_dimension(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create region dimension table using business IDs"""
        logger.info("Creating region dimension...")
        regions = data.get('regions', pd.DataFrame())
        
        if regions.empty:
            dim_region = pd.DataFrame({
                'region_id': ['default'], 'region_name': ['Default'],
                'country': ['Unknown'], 'continent': ['Unknown'],
                'created_at': [datetime.now()], 'updated_at': [datetime.now()]
            })
        else:
            id_col = 'regionId' if 'regionId' in regions.columns else '_id'
            dim_region = pd.DataFrame()
            dim_region['region_id'] = regions[id_col].astype(str)
            dim_region['region_name'] = regions['regionName'] if 'regionName' in regions.columns else 'Unknown'
            dim_region['country'] = regions['country'] if 'country' in regions.columns else 'Unknown'
            dim_region['continent'] = regions['continent'] if 'continent' in regions.columns else 'Unknown'
            dim_region['created_at'] = pd.to_datetime(regions.get('createdAt', datetime.now()), errors='coerce')
            dim_region['updated_at'] = pd.to_datetime(regions.get('updatedAt', datetime.now()), errors='coerce')
        
        dim_region = dim_region.drop_duplicates(subset=['region_id'])
        logger.info(f"  Created region dimension with {len(dim_region)} regions")
        return dim_region
    
    def create_fact_sales(self, data: Dict[str, pd.DataFrame], dimensions: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create fact sales table with standardized business ID joins"""
        logger.info("Creating fact sales table...")
        orders = data['orders'].copy()
        items = data['orderitems'].copy()
        users = data['users'].copy()
        
        orders['order_join_key'] = orders['orderId'].astype(str)
        items['order_join_key'] = items['orderId'].astype(str)
        
        if 'status' in orders.columns:
            excluded = [s.upper() for s in self.config.EXCLUDED_ORDER_STATUSES]
            orders = orders[~orders['status'].str.upper().isin(excluded)]
        
        # 1. Join Items and Orders
        order_cols = ['order_join_key', 'userId', 'orderDate']
        fact = items.merge(orders[order_cols], on='order_join_key', how='inner')
        
        # 2. Add Region Info from Users (using userId)
        user_id_col = 'userId' if 'userId' in users.columns else '_id'
        users[user_id_col] = users[user_id_col].astype(str)
        fact['user_join_key'] = fact['userId'].astype(str)
        
        if 'regionId' in users.columns:
            fact = fact.merge(users[[user_id_col, 'regionId']].rename(columns={user_id_col: 'user_join_key'}), on='user_join_key', how='left')
        else:
            fact['regionId'] = 'default'
        
        # 3. Add Product Info
        fact['product_join_key'] = fact['productId'].astype(str)
        fact = fact.merge(dimensions['dim_product'][['product_id', 'price', 'cost']], left_on='product_join_key', right_on='product_id', how='left')
        
        # 4. Date conversion
        fact['date_dt'] = pd.to_datetime(fact['orderDate'], errors='coerce')
        fact['date_id'] = (fact['date_dt'].dt.year * 10000 + fact['date_dt'].dt.month * 100 + fact['date_dt'].dt.day).fillna(0).astype(int)
        
        qty_col = 'quantity' if 'quantity' in fact.columns else 'qty'
        up_col = 'unitPrice' if 'unitPrice' in fact.columns else 'price'
        uc_col = 'unitCost' if 'unitCost' in fact.columns else 'cost'
        
        fact['qty_val'] = pd.to_numeric(fact[qty_col], errors='coerce').fillna(1) if qty_col in fact.columns else 1
        fact['price_val'] = pd.to_numeric(fact[up_col], errors='coerce').fillna(0) if up_col in fact.columns else 0
        fact['cost_val'] = pd.to_numeric(fact[uc_col], errors='coerce').fillna(0) if uc_col in fact.columns else 0
        
        fact['revenue'] = fact['qty_val'] * fact['price_val']
        fact['cost_amount'] = fact['qty_val'] * fact['cost_val']
        fact['profit'] = fact['revenue'] - fact['cost_amount']
        fact['margin_pct'] = np.where(fact['revenue'] > 0, (fact['profit'] / fact['revenue']) * 100, 0)
        
        fact_sales = pd.DataFrame()
        fact_sales['order_id'] = fact['order_join_key']
        fact_sales['order_item_id'] = fact['orderItemId'].astype(str) if 'orderItemId' in fact.columns else fact.index.astype(str)
        fact_sales['date_id'] = fact['date_id']
        fact_sales['product_id'] = fact['product_id'].fillna('unknown')
        fact_sales['customer_id'] = fact['user_join_key']
        fact_sales['region_id'] = fact['regionId'].fillna('default').astype(str)
        fact_sales['quantity'] = fact['qty_val'].astype(int)
        fact_sales['unit_price'] = fact['price_val'].round(2)
        fact_sales['revenue'] = fact['revenue'].round(2)
        fact_sales['cost_amount'] = fact['cost_amount'].round(2)
        fact_sales['profit'] = fact['revenue'] - fact['cost_amount']
        fact_sales['margin_pct'] = fact['margin_pct'].round(2)
        
        # Referential Integrity Filtering
        initial_count = len(fact_sales)
        fact_sales = fact_sales[
            fact_sales['customer_id'].isin(dimensions['dim_customer']['customer_id']) &
            fact_sales['product_id'].isin(dimensions['dim_product']['product_id']) &
            fact_sales['region_id'].isin(dimensions['dim_region']['region_id']) &
            fact_sales['date_id'].isin(dimensions['dim_date']['date_id'])
        ]
        
        removed = initial_count - len(fact_sales)
        if removed > 0:
            logger.warning(f"  Removed {removed} rows due to integrity violations")
            
        logger.info(f"  Created fact sales: {len(fact_sales)} rows")
        return fact_sales
    
    def transform_all(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
        """Execute complete transformation pipeline"""
        logger.info("\n" + "="*50)
        logger.info("STARTING TRANSFORMATION")
        logger.info("="*50 + "\n")
        
        dimensions = {
            'dim_date': self.create_date_dimension(data),
            'dim_product': self.create_product_dimension(data),
            'dim_customer': self.create_customer_dimension(data),
            'dim_region': self.create_region_dimension(data)
        }
        
        fact_sales = self.create_fact_sales(data, dimensions)
        
        return dimensions, fact_sales


def main():
    """Test transformation module"""
    from extract import MongoExtractor
    
    # Extract data
    extractor = MongoExtractor()
    data = extractor.extract_all_collections()
    
    # Transform data
    transformer = DataTransformer()
    dimensions, fact_sales = transformer.transform_all(data)
    
    # Display results
    print("\n=== TRANSFORMATION RESULTS ===")
    for name, df in dimensions.items():
        print(f"\n{name}:")
        print(df.head())
    
    print("\nfact_sales:")
    print(fact_sales.head())


if __name__ == "__main__":
    main()
