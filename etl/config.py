"""
Configuration Management for ETL Pipeline
Handles database connections, logging, and runtime parameters
"""

import os
import re
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration class for ETL pipeline"""
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'ecommerce')
    
    # PostgreSQL Configuration
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = os.getenv('PG_PORT', '5432')
    PG_DATABASE = os.getenv('PG_DATABASE', 'ecommerce_dw')
    PG_USER = os.getenv('PG_USER', 'bi_admin')
    PG_PASSWORD = os.getenv('PG_PASSWORD', 'change_me')
    
    # PostgreSQL Connection String (DATABASE_URL overrides the individual settings)
    @property
    def PG_CONNECTION_STRING(self):
        return os.getenv('DATABASE_URL') or (
            f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
        )
    
    # ETL Configuration
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # MongoDB Collections
    COLLECTIONS = [
        'users',
        'products',
        'orders',
        'orderitems',  # Note: no underscore
        'payments',
        'regions',
        'categories'
    ]
    
    # Business Rules
    EXCLUDED_ORDER_STATUSES = ['cancelled', 'refunded', 'failed']
    REQUIRED_PAYMENT_STATUS = 'completed'


def mask_uri(uri: str) -> str:
    """Hide the user and password in a connection string before logging it."""
    return re.sub(r"//[^/@]+@", "//***:***@", uri or "")


def setup_logging(log_file='etl_pipeline.log'):
    """
    Configure logging for ETL pipeline
    
    Args:
        log_file: Path to log file
    """
    config = Config()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_path = log_dir / log_file
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('ETL_Pipeline')


# Create global logger instance
logger = setup_logging()


if __name__ == "__main__":
    # Test configuration
    config = Config()
    print("Configuration Test:")
    print(f"MongoDB URI: {mask_uri(config.MONGO_URI)}")
    print(f"MongoDB Database: {config.MONGO_DB}")
    print(f"PostgreSQL Connection: {mask_uri(config.PG_CONNECTION_STRING)}")
    print(f"Batch Size: {config.BATCH_SIZE}")
    print(f"Collections to Extract: {config.COLLECTIONS}")
