import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from etl.extractors.raw_data_extractor import RawDataExtractor
from etl.transformers.data_cleaner import DataCleaner
from etl.transformers.data_validator import DataValidator
from etl.loaders.clean_data_loader import CleanDataLoader

class VehicleETLPipeline:
    def __init__(self):
        self.extractor = RawDataExtractor()
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.loader = CleanDataLoader()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for the ETL process"""
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_full_pipeline(self):
        """Run the complete ETL pipeline"""
        try:
            self.logger.info("Starting ETL pipeline...")
            
            # Extract
            self.logger.info("Extracting raw data...")
            raw_data = self.extractor.extract_all_vehicles()
            self.logger.info(f"Extracted {len(raw_data)} records")
            
            if raw_data.empty:
                self.logger.warning("No data to process")
                return
            
            # Validate raw data
            self.logger.info("Validating raw data...")
            validation_report = self.validator.validate_data(raw_data)
            self.log_validation_report(validation_report)
            
            # Transform
            self.logger.info("Cleaning and transforming data...")
            clean_data = self.cleaner.clean_data(raw_data)
            self.logger.info(f"Cleaned data: {len(clean_data)} records")
            
            # Validate clean data
            self.logger.info("Validating cleaned data...")
            clean_validation = self.validator.validate_data(clean_data)
            self.log_validation_report(clean_validation, "CLEAN DATA")
            
            # Load
            self.logger.info("Loading clean data...")
            self.loader.load_clean_data(clean_data, mode='replace')
            
            # Quality check
            self.logger.info("Generating quality report...")
            stats = self.loader.get_data_quality_stats()
            self.log_quality_stats(stats)
            
            self.logger.info("ETL pipeline completed successfully")
            return stats
            
        except Exception as e:
            self.logger.error(f"ETL pipeline failed: {str(e)}")
            raise
    
    def run_incremental_pipeline(self, hours: int = 24):
        """Run incremental ETL for recent data"""
        try:
            self.logger.info(f"Starting incremental ETL for last {hours} hours...")
            
            # Extract recent data
            raw_data = self.extractor.extract_recent_vehicles(hours)
            self.logger.info(f"Extracted {len(raw_data)} recent records")
            
            if raw_data.empty:
                self.logger.info("No new data to process")
                return
            
            # Transform
            clean_data = self.cleaner.clean_data(raw_data)
            
            # Load (append mode for incremental)
            self.loader.load_clean_data(clean_data, mode='append')
            
            self.logger.info("Incremental ETL completed successfully")
            
        except Exception as e:
            self.logger.error(f"Incremental ETL failed: {str(e)}")
            raise
    
    def log_quality_stats(self, stats: dict):
        """Log data quality statistics"""
        self.logger.info("=== DATA QUALITY REPORT ===")
        self.logger.info(f"Total records: {stats['total_records']}")
        self.logger.info(f"Price issues: {stats['price_issues']}")
        
        self.logger.info("Missing data percentages:")
        for field, percentage in stats['missing_percentages'].items():
            self.logger.info(f"  {field}: {percentage:.2f}%")
        
        self.logger.info("Top brands:")
        for brand_info in stats['brand_distribution'][:5]:
            self.logger.info(f"  {brand_info['brand']}: {brand_info['count']} vehicles")
    
    def log_validation_report(self, report: dict, title: str = "RAW DATA"):
        """Log validation report"""
        self.logger.info(f"=== {title} VALIDATION ====")
        self.logger.info(f"Total records: {report['total_records']}")
        self.logger.info(f"Validation passed: {report['passed_validation']}")
        
        if report['validation_errors']:
            self.logger.error("Validation errors:")
            for error in report['validation_errors']:
                self.logger.error(f"  {error}")
        
        if report['warnings']:
            self.logger.warning("Validation warnings:")
            for warning in report['warnings']:
                self.logger.warning(f"  {warning}")

if __name__ == "__main__":
    pipeline = VehicleETLPipeline()
    pipeline.run_full_pipeline()