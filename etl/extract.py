"""
Data Extraction Module
Extracts data from MongoDB operational database
"""

import pandas as pd
from pymongo import MongoClient
from typing import Dict, List
from .config import Config, logger, mask_uri


class MongoExtractor:
    """Handles data extraction from MongoDB"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.config = Config()
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB: {mask_uri(self.config.MONGO_URI)}")
            self.client = MongoClient(self.config.MONGO_URI)
            self.db = self.client[self.config.MONGO_DB]
            
            # Test connection
            self.client.server_info()
            logger.info(f"Successfully connected to MongoDB database: {self.config.MONGO_DB}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def extract_collection(self, collection_name: str) -> pd.DataFrame:
        """
        Extract data from a MongoDB collection
        
        Args:
            collection_name: Name of the collection to extract
            
        Returns:
            pandas DataFrame with collection data
        """
        try:
            logger.info(f"Extracting data from collection: {collection_name}")
            
            # Get collection
            collection = self.db[collection_name]
            
            # Get document count
            count = collection.count_documents({})
            logger.info(f"Found {count} documents in {collection_name}")
            
            if count == 0:
                logger.warning(f"No data found in {collection_name}")
                return pd.DataFrame()
            
            # Extract all documents
            cursor = collection.find({})
            
            # Convert to DataFrame
            df = pd.DataFrame(list(cursor))
            
            # Convert MongoDB _id to string if present
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
            
            logger.info(f"Successfully extracted {len(df)} rows from {collection_name}")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting {collection_name}: {str(e)}")
            raise
    
    def extract_all_collections(self) -> Dict[str, pd.DataFrame]:
        """
        Extract all required collections
        
        Returns:
            Dictionary mapping collection names to DataFrames
        """
        data = {}
        
        try:
            self.connect()
            
            for collection_name in self.config.COLLECTIONS:
                df = self.extract_collection(collection_name)
                data[collection_name] = df
            
            # Log summary
            logger.info("\n" + "="*50)
            logger.info("EXTRACTION SUMMARY")
            logger.info("="*50)
            for collection_name, df in data.items():
                logger.info(f"{collection_name}: {len(df)} rows")
            logger.info("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            raise
        
        finally:
            self.disconnect()
        
        return data
    
    def validate_extracted_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate extracted data
        
        Args:
            data: Dictionary of DataFrames
            
        Returns:
            True if validation passes
        """
        logger.info("Validating extracted data...")
        
        validation_passed = True
        
        # Check each collection was extracted
        for collection_name in self.config.COLLECTIONS:
            if collection_name not in data:
                logger.error(f"Missing collection: {collection_name}")
                validation_passed = False
            elif data[collection_name].empty:
                logger.warning(f"Empty collection: {collection_name}")
        
        # Check critical collections have data
        critical_collections = ['orders', 'orderitems', 'products', 'users']
        for collection_name in critical_collections:
            if collection_name in data and len(data[collection_name]) == 0:
                logger.error(f"Critical collection {collection_name} is empty!")
                validation_passed = False
        
        if validation_passed:
            logger.info("✓ Data validation passed")
        else:
            logger.error("✗ Data validation failed")
        
        return validation_passed


def main():
    """Test extraction module"""
    extractor = MongoExtractor()
    
    try:
        # Extract all collections
        data = extractor.extract_all_collections()
        
        # Validate
        extractor.validate_extracted_data(data)
        
        # Display sample data
        for collection_name, df in data.items():
            if not df.empty:
                print(f"\n{collection_name} sample:")
                print(df.head(3))
                print(f"Shape: {df.shape}")
        
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
