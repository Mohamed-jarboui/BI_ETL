"""
ETL Pipeline Main Orchestrator
Coordinates Extract, Transform, Load operations
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add etl directory to path
sys.path.insert(0, str(Path(__file__).parent))

from .config import Config, logger
from .extract import MongoExtractor
from .transform import DataTransformer
from .load import DataWarehouseLoader


class ETLPipeline:
    """Main ETL Pipeline orchestrator"""
    
    def __init__(self):
        """Initialize ETL pipeline"""
        self.config = Config()
        self.extractor = MongoExtractor()
        self.transformer = DataTransformer()
        self.loader = DataWarehouseLoader()
        
        self.start_time = None
        self.end_time = None
    
    def run(self, extract=True, transform=True, load=True):
        """
        Run ETL pipeline
        
        Args:
            extract: Run extraction phase
            transform: Run transformation phase
            load: Run loading phase
        """
        self.start_time = datetime.now()
        
        logger.info("\n" + "="*60)
        logger.info("ETL PIPELINE STARTED")
        logger.info(f"Start Time: {self.start_time}")
        logger.info("="*60 + "\n")
        
        try:
            # Phase 1: Extract
            if extract:
                logger.info("PHASE 1: EXTRACTION")
                data = self.extractor.extract_all_collections()
                
                if not self.extractor.validate_extracted_data(data):
                    raise ValueError("Data extraction validation failed")
            else:
                logger.info("Skipping extraction phase")
                data = {}
            
            # Phase 2: Transform
            if transform:
                logger.info("\nPHASE 2: TRANSFORMATION")
                dimensions, fact_sales = self.transformer.transform_all(data)
            else:
                logger.info("Skipping transformation phase")
                dimensions, fact_sales = {}, None
            
            # Phase 3: Load
            if load:
                logger.info("\nPHASE 3: LOADING")
                self.loader.load_all(dimensions, fact_sales)
            else:
                logger.info("Skipping loading phase")
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            logger.info("\n" + "="*60)
            logger.info("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"End Time: {self.end_time}")
            logger.info(f"Duration: {duration}")
            logger.info("="*60 + "\n")
            
            return True
            
        except Exception as e:
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            logger.error("\n" + "="*60)
            logger.error("✗ ETL PIPELINE FAILED")
            logger.error(f"Error: {str(e)}")
            logger.error(f"Duration before failure: {duration}")
            logger.error("="*60 + "\n")
            
            raise


def main():
    """Main entry point with CLI arguments"""
    parser = argparse.ArgumentParser(description='E-commerce ETL Pipeline')
    
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Run only extraction phase'
    )
    
    parser.add_argument(
        '--transform-only',
        action='store_true',
        help='Run only transformation phase (requires prior extraction)'
    )
    
    parser.add_argument(
        '--load-only',
        action='store_true',
        help='Run only loading phase (requires prior extract and transform)'
    )
    
    parser.add_argument(
        '--skip-extract',
        action='store_true',
        help='Skip extraction phase'
    )
    
    parser.add_argument(
        '--skip-transform',
        action='store_true',
        help='Skip transformation phase'
    )
    
    parser.add_argument(
        '--skip-load',
        action='store_true',
        help='Skip loading phase'
    )
    
    args = parser.parse_args()
    
    # Determine which phases to run
    extract = not args.skip_extract
    transform = not args.skip_transform
    load = not args.skip_load
    
    if args.extract_only:
        extract, transform, load = True, False, False
    elif args.transform_only:
        extract, transform, load = False, True, False
    elif args.load_only:
        extract, transform, load = False, False, True
    
    # Run pipeline
    pipeline = ETLPipeline()
    
    try:
        pipeline.run(extract=extract, transform=transform, load=load)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
