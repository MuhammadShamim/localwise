"""
Sample Python module for testing code processing capabilities.

This module demonstrates various Python constructs including:
- Classes and inheritance
- Functions and methods  
- Decorators and properties
- Exception handling
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class DataProcessor:
    """A sample data processor class for demonstration."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Initialize the data processor.
        
        Args:
            name: Name of the processor
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.processed_count = 0
        self.created_at = datetime.now()
    
    @property
    def is_configured(self) -> bool:
        """Check if processor is properly configured."""
        return bool(self.config)
    
    def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        Process a list of data records.
        
        Args:
            data: List of dictionaries to process
            
        Returns:
            Processed data records
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        try:
            processed = []
            for record in data:
                processed_record = self._process_record(record)
                processed.append(processed_record)
                self.processed_count += 1
            
            logger.info(f"Processed {len(processed)} records")
            return processed
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
    
    def _process_record(self, record: Dict) -> Dict:
        """Process a single record (private method)."""
        # Add processing timestamp
        record["processed_at"] = datetime.now().isoformat()
        record["processor"] = self.name
        
        # Apply any configured transformations
        if "transformations" in self.config:
            for transform in self.config["transformations"]:
                record = self._apply_transformation(record, transform)
        
        return record
    
    def _apply_transformation(self, record: Dict, transform: str) -> Dict:
        """Apply a transformation to a record."""
        if transform == "uppercase_name":
            if "name" in record:
                record["name"] = record["name"].upper()
        elif transform == "add_id":
            record["id"] = f"{self.name}_{self.processed_count}"
        
        return record
    
    def get_stats(self) -> Dict[str, any]:
        """Get processor statistics."""
        return {
            "name": self.name,
            "processed_count": self.processed_count,
            "created_at": self.created_at.isoformat(),
            "is_configured": self.is_configured
        }

def create_processor(name: str, **kwargs) -> DataProcessor:
    """Factory function to create a configured processor."""
    config = {
        "transformations": kwargs.get("transformations", []),
        "batch_size": kwargs.get("batch_size", 100),
        "timeout": kwargs.get("timeout", 30)
    }
    
    return DataProcessor(name, config)

# Example usage
if __name__ == "__main__":
    # Create a processor
    processor = create_processor(
        "sample_processor",
        transformations=["uppercase_name", "add_id"],
        batch_size=50
    )
    
    # Sample data
    sample_data = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Jane", "age": 25, "city": "Los Angeles"},
        {"name": "Bob", "age": 35, "city": "Chicago"}
    ]
    
    # Process the data
    try:
        results = processor.process_data(sample_data)
        print("Processing completed:", json.dumps(results, indent=2))
        print("Stats:", processor.get_stats())
    except Exception as e:
        print(f"Error: {str(e)}")
