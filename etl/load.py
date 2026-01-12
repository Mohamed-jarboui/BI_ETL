"""
Data Loading Module
Loads transformed data into PostgreSQL Data Warehouse
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict
from .config import Config, logger


class DataWarehouseLoader:
    """Handles loading data into PostgreSQL Data Warehouse"""
    
    def __init__(self):
        """Initialize loader"""
        self.config = Config()
        self.engine = None
    
    def connect(self):
        """Create connection to PostgreSQL"""
        try:
            logger.info(f"Connecting to PostgreSQL: {self.config.PG_HOST}:{self.config.PG_PORT}")
            self.engine = create_engine(self.config.PG_CONNECTION_STRING)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"Successfully connected to PostgreSQL")
                logger.info(f"  Version: {version[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise
    
    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL connection closed")
    
    def truncate_table(self, table_name: str):
        """
        Truncate a table
        
        Args:
            table_name: Name of table to truncate
        """
        try:
            with self.engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE;"))
                logger.info(f"  Truncated table: {table_name}")
        except Exception as e:
            logger.error(f"  CRITICAL: Could not truncate {table_name}: {str(e)}")
            raise
    
    def load_dimension(self, df: pd.DataFrame, table_name: str, truncate: bool = True):
        """
        Load dimension table
        
        Args:
            df: DataFrame to load
            table_name: Target table name
            truncate: Whether to truncate before loading
        """
        try:
            logger.info(f"Loading {table_name}...")
            
            # Check for duplicates in the dataframe
            pk_map = {
                'dim_date': 'date_id',
                'dim_product': 'product_id',
                'dim_customer': 'customer_id',
                'dim_region': 'region_id',
                'fact_sales': 'sale_id'
            }
            
            pk = pk_map.get(table_name)
            if pk and pk in df.columns:
                dupes = df[df.duplicated(subset=[pk])]
                if not dupes.empty:
                    logger.error(f"  Found {len(dupes)} duplicate keys in {table_name} for column {pk}!")
                    logger.error(f"  Sample duplicates: {dupes[pk].head().tolist()}")
            
            if truncate:
                self.truncate_table(table_name)
            
            # Load data
            rows_loaded = df.to_sql(
                table_name,
                self.engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=self.config.BATCH_SIZE
            )
            
            logger.info(f"  ✓ Loaded {len(df)} rows into {table_name}")
            
            # Verify load
            self.verify_table_load(table_name, len(df))
            
        except Exception as e:
            logger.error(f"  ✗ Error loading {table_name}: {str(e)}")
            raise
    
    def load_fact_table(self, df: pd.DataFrame, table_name: str = 'fact_sales', truncate: bool = True):
        """
        Load fact table with batching
        
        Args:
            df: DataFrame to load
            table_name: Target table name
            truncate: Whether to truncate before loading
        """
        try:
            logger.info(f"Loading {table_name}...")
            
            if truncate:
                self.truncate_table(table_name)
            
            # Load in batches
            total_rows = len(df)
            batch_size = self.config.BATCH_SIZE
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                
                batch.to_sql(
                    table_name,
                    self.engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                
                logger.info(f"  Loaded batch {i//batch_size + 1}: {len(batch)} rows")
            
            logger.info(f"  ✓ Loaded {total_rows} rows into {table_name}")
            
            # Verify load
            self.verify_table_load(table_name, total_rows)
            
        except Exception as e:
            logger.error(f"  ✗ Error loading {table_name}: {str(e)}")
            raise
    
    def verify_table_load(self, table_name: str, expected_count: int):
        """
        Verify data was loaded correctly
        
        Args:
            table_name: Table to verify
            expected_count: Expected row count
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
                actual_count = result.fetchone()[0]
                
                if actual_count == expected_count:
                    logger.info(f"  ✓ Verification passed: {actual_count} rows")
                else:
                    logger.warning(f"  ⚠ Row count mismatch: expected {expected_count}, got {actual_count}")
        
        except Exception as e:
            logger.error(f"  Error verifying {table_name}: {str(e)}")
    
    def run_data_quality_checks(self):
        """Run data quality checks after loading"""
        logger.info("\nRunning data quality checks...")
        
        checks = [
            {
                'name': 'Orphaned Sales Records',
                'query': """
                    SELECT COUNT(*) 
                    FROM fact_sales fs
                    LEFT JOIN dim_product dp ON fs.product_id = dp.product_id
                    WHERE dp.product_id IS NULL;
                """
            },
            {
                'name': 'Invalid Date References',
                'query': """
                    SELECT COUNT(*)
                    FROM fact_sales fs
                    LEFT JOIN dim_date dd ON fs.date_id = dd.date_id
                    WHERE dd.date_id IS NULL;
                """
            },
            {
                'name': 'Negative Revenue',
                'query': "SELECT COUNT(*) FROM fact_sales WHERE revenue < 0;"
            },
            {
                'name': 'Zero Quantity Sales',
                'query': "SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0;"
            }
        ]
        
        all_passed = True
        
        try:
            with self.engine.connect() as conn:
                for check in checks:
                    result = conn.execute(text(check['query']))
                    count = result.fetchone()[0]
                    
                    if count == 0:
                        logger.info(f"  ✓ {check['name']}: PASSED")
                    else:
                        logger.warning(f"  ✗ {check['name']}: FAILED ({count} issues)")
                        all_passed = False
        
        except Exception as e:
            logger.error(f"Error running quality checks: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def get_summary_statistics(self):
        """Get summary statistics from loaded data"""
        logger.info("\nGenerating summary statistics...")
        
        queries = {
            'Total Orders': "SELECT COUNT(DISTINCT order_id) FROM fact_sales;",
            'Total Revenue': "SELECT ROUND(SUM(revenue)::numeric, 2) FROM fact_sales;",
            'Total Profit': "SELECT ROUND(SUM(profit)::numeric, 2) FROM fact_sales;",
            'Average Margin %': "SELECT ROUND(AVG(margin_pct)::numeric, 2) FROM fact_sales;",
            'Total Products': "SELECT COUNT(*) FROM dim_product;",
            'Total Customers': "SELECT COUNT(*) FROM dim_customer;",
            'Total Regions': "SELECT COUNT(*) FROM dim_region;",
            'Date Range': "SELECT MIN(date) || ' to ' || MAX(date) FROM dim_date;",
        }
        
        try:
            with self.engine.connect() as conn:
                logger.info("  " + "="*40)
                for name, query in queries.items():
                    result = conn.execute(text(query))
                    value = result.fetchone()[0]
                    logger.info(f"  {name}: {value}")
                logger.info("  " + "="*40)
        
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
    
    def load_all(self, dimensions: Dict[str, pd.DataFrame], fact_sales: pd.DataFrame):
        """
        Load all data into Data Warehouse
        
        Args:
            dimensions: Dictionary of dimension DataFrames
            fact_sales: Fact sales DataFrame
        """
        logger.info("\n" + "="*50)
        logger.info("LOADING DATA TO DATA WAREHOUSE")
        logger.info("="*50 + "\n")
        
        try:
            self.connect()
            
            # Load dimensions first (referenced by fact table)
            for table_name, df in dimensions.items():
                self.load_dimension(df, table_name, truncate=True)
            
            # Load fact table
            self.load_fact_table(fact_sales, 'fact_sales', truncate=True)
            
            # Run quality checks
            checks_passed = self.run_data_quality_checks()
            
            # Get summary
            self.get_summary_statistics()
            
            logger.info("\n" + "="*50)
            if checks_passed:
                logger.info("✓ DATA WAREHOUSE LOAD COMPLETED SUCCESSFULLY")
            else:
                logger.warning("⚠ DATA WAREHOUSE LOADED WITH WARNINGS")
            logger.info("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Load failed: {str(e)}")
            raise
        
        finally:
            self.disconnect()


def main():
    """Test loading module"""
    from extract import MongoExtractor
    from transform import DataTransformer
    
    # Extract
    extractor = MongoExtractor()
    data = extractor.extract_all_collections()
    
    # Transform
    transformer = DataTransformer()
    dimensions, fact_sales = transformer.transform_all(data)
    
    # Load
    loader = DataWarehouseLoader()
    loader.load_all(dimensions, fact_sales)


if __name__ == "__main__":
    main()
