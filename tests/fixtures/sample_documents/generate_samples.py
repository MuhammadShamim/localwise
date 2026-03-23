import os
import json
from pathlib import Path

# Get the current directory (fixtures/sample_documents)
current_dir = Path(__file__).parent

# Write various sample documents for testing

# 1. Sample README.md
readme_content = """# Sample Project Documentation

## Overview
This is a sample project documentation file for testing LocalWise functionality.

## Features
- Document processing
- AI-powered querying
- Knowledge base management

## Installation
1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run the application

## Usage
The system can process various file formats including:
- Markdown files
- PDF documents
- CSV data files
- JSON configuration files

## Contributing
Please read our contributing guidelines before submitting changes.

## License
This project is licensed under the MIT License.
"""

with open(current_dir / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

# 2. Sample JSON configuration
config_data = {
    "application": {
        "name": "Sample Application",
        "version": "1.0.0",
        "debug": False
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "sample_db",
        "credentials": {
            "username": "user",
            "password": "password"
        }
    },
    "features": {
        "authentication": True,
        "logging": True,
        "caching": False
    },
    "settings": {
        "max_file_size": "10MB",
        "allowed_formats": ["pdf", "docx", "txt", "md"],
        "timeout": 30
    }
}

with open(current_dir / "config.json", "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2)

# 3. Sample CSV data
csv_content = """id,name,email,department,salary,join_date
1,John Doe,john.doe@company.com,Engineering,75000,2023-01-15
2,Jane Smith,jane.smith@company.com,Marketing,65000,2023-02-01
3,Bob Johnson,bob.johnson@company.com,Sales,70000,2023-01-20
4,Alice Brown,alice.brown@company.com,Engineering,80000,2022-12-10
5,Charlie Wilson,charlie.wilson@company.com,HR,60000,2023-03-01
6,Diana Davis,diana.davis@company.com,Finance,72000,2023-01-30
7,Frank Miller,frank.miller@company.com,Engineering,78000,2022-11-15
8,Grace Lee,grace.lee@company.com,Marketing,68000,2023-02-15
9,Henry Taylor,henry.taylor@company.com,Operations,64000,2023-01-05
10,Ivy Chen,ivy.chen@company.com,Engineering,82000,2022-10-20
"""

with open(current_dir / "employees.csv", "w", encoding="utf-8") as f:
    f.write(csv_content)

# 4. Sample YAML configuration
yaml_content = """# Application Configuration
application:
  name: Sample YAML App
  version: 1.0.0
  environment: production

server:
  host: 0.0.0.0
  port: 8080
  ssl: false

database:
  type: postgresql
  connection:
    host: localhost
    port: 5432
    database: yamlapp
    pool_size: 10

logging:
  level: info
  format: json
  outputs:
    - console
    - file

features:
  authentication:
    enabled: true
    provider: oauth2
  caching:
    enabled: true
    type: redis
    ttl: 3600
  monitoring:
    enabled: true
    endpoint: /metrics

security:
  cors:
    enabled: true
    origins:
      - https://app.example.com
      - https://api.example.com
  rate_limiting:
    enabled: true
    requests_per_minute: 100
"""

with open(current_dir / "app_config.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_content)

# 5. Sample Python code
python_content = '''"""
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
'''

with open(current_dir / "sample_code.py", "w", encoding="utf-8") as f:
    f.write(python_content)

# 6. Sample XML document
xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<library>
    <metadata>
        <name>Sample Library</name>
        <version>1.0</version>
        <created>2024-01-15</created>
        <description>A sample XML document for testing</description>
    </metadata>
    
    <books>
        <book id="book1" genre="fiction">
            <title>The Great Adventure</title>
            <author>
                <first_name>John</first_name>
                <last_name>Author</last_name>
            </author>
            <publication>
                <year>2023</year>
                <publisher>Sample Publishing</publisher>
                <isbn>978-1234567890</isbn>
            </publication>
            <description>
                An exciting tale of adventure and discovery in uncharted territories.
            </description>
        </book>
        
        <book id="book2" genre="technology">
            <title>Modern Software Development</title>
            <author>
                <first_name>Jane</first_name>
                <last_name>Developer</last_name>
            </author>
            <publication>
                <year>2023</year>
                <publisher>Tech Books Inc</publisher>
                <isbn>978-9876543210</isbn>
            </publication>
            <description>
                A comprehensive guide to modern software development practices and methodologies.
            </description>
        </book>
        
        <book id="book3" genre="science">
            <title>Quantum Computing Basics</title>
            <author>
                <first_name>Dr. Alice</first_name>
                <last_name>Scientist</last_name>
            </author>
            <publication>
                <year>2023</year>
                <publisher>Science Press</publisher>
                <isbn>978-1122334455</isbn>
            </publication>
            <description>
                An introduction to the fascinating world of quantum computing and its applications.
            </description>
        </book>
    </books>
    
    <categories>
        <category name="fiction">
            <description>Fictional literature and stories</description>
            <book_count>1</book_count>
        </category>
        <category name="technology">
            <description>Technology and programming books</description>
            <book_count>1</book_count>
        </category>
        <category name="science">
            <description>Scientific and research publications</description>
            <book_count>1</book_count>
        </category>
    </categories>
</library>
'''

with open(current_dir / "library.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)

# 7. Sample text document
text_content = """Sample Text Document for Testing

This is a plain text document that contains various types of content
for testing the LocalWise knowledge assistant system.

INTRODUCTION
============

LocalWise is an AI-powered knowledge assistant that can process
and understand various types of documents. This sample text file
demonstrates how plain text content is handled by the system.

KEY FEATURES
============

1. Document Processing
   - Supports multiple file formats
   - Extracts meaningful content
   - Creates searchable knowledge base

2. AI Integration
   - Uses local language models
   - No external API dependencies
   - Maintains data privacy

3. Query Capabilities
   - Natural language questions
   - Context-aware responses
   - Source attribution

TECHNICAL DETAILS
=================

The system utilizes vector embeddings to create semantic
representations of document content. This allows for:

- Similarity-based retrieval
- Context-aware question answering
- Semantic search capabilities

USAGE EXAMPLES
==============

Users can ask questions like:
- "What are the key features of LocalWise?"
- "How does the AI integration work?"
- "What file formats are supported?"

The system will search through processed documents
and provide relevant answers with source citations.

CONCLUSION
==========

This sample document demonstrates the variety of content
that can be processed and made searchable through the
LocalWise knowledge assistant system.

For more information, see the documentation and examples
provided with the system.
"""

with open(current_dir / "sample_text.txt", "w", encoding="utf-8") as f:
    f.write(text_content)

print("✅ Generated sample test documents:")
print(f"   - {current_dir}/README.md")
print(f"   - {current_dir}/config.json") 
print(f"   - {current_dir}/employees.csv")
print(f"   - {current_dir}/app_config.yaml")
print(f"   - {current_dir}/sample_code.py")
print(f"   - {current_dir}/library.xml")
print(f"   - {current_dir}/sample_text.txt")