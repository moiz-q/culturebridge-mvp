"""
Script to export data from Bubble API to CSV files.

Requirements: 10.1
"""
import requests
import csv
import json
import os
from typing import List, Dict, Any
from datetime import datetime
import logging

from migration.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BubbleExporter:
    """Export data from Bubble API to CSV files"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        Initialize Bubble exporter.
        
        Args:
            api_url: Bubble API base URL
            api_key: Bubble API authentication key
        """
        self.api_url = api_url or config.BUBBLE_API_URL
        self.api_key = api_key or config.BUBBLE_API_KEY
        self.export_dir = config.EXPORT_DIR
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Validate configuration
        if not self.api_key:
            raise ValueError("BUBBLE_API_KEY environment variable must be set")
    
    def _make_request(self, endpoint: str, cursor: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Make authenticated request to Bubble API.
        
        Args:
            endpoint: API endpoint path
            cursor: Pagination cursor
            limit: Number of records per page
            
        Returns:
            API response as dictionary
        """
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        params = {
            "cursor": cursor,
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {endpoint}: {str(e)}")
            raise
    
    def export_endpoint(self, endpoint_name: str, endpoint_path: str) -> str:
        """
        Export all data from a Bubble endpoint to CSV.
        
        Args:
            endpoint_name: Name for the export file
            endpoint_path: API endpoint path
            
        Returns:
            Path to exported CSV file
        """
        logger.info(f"Starting export of {endpoint_name}...")
        
        all_records = []
        cursor = 0
        batch_size = config.BATCH_SIZE
        
        while True:
            try:
                response = self._make_request(endpoint_path, cursor=cursor, limit=batch_size)
                records = response.get("response", {}).get("results", [])
                
                if not records:
                    break
                
                all_records.extend(records)
                logger.info(f"Fetched {len(records)} records (total: {len(all_records)})")
                
                # Check if there are more records
                remaining = response.get("response", {}).get("remaining", 0)
                if remaining == 0:
                    break
                
                cursor += batch_size
                
            except Exception as e:
                logger.error(f"Error during export: {str(e)}")
                break
        
        # Write to CSV
        if all_records:
            csv_path = os.path.join(self.export_dir, f"{endpoint_name}.csv")
            self._write_csv(csv_path, all_records)
            logger.info(f"Exported {len(all_records)} records to {csv_path}")
            return csv_path
        else:
            logger.warning(f"No records found for {endpoint_name}")
            return ""
    
    def _write_csv(self, filepath: str, records: List[Dict[str, Any]]):
        """
        Write records to CSV file.
        
        Args:
            filepath: Path to CSV file
            records: List of record dictionaries
        """
        if not records:
            return
        
        # Get all unique keys from all records
        fieldnames = set()
        for record in records:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                # Convert complex types to JSON strings
                row = {}
                for key, value in record.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)
    
    def export_all(self) -> Dict[str, str]:
        """
        Export all data from Bubble API.
        
        Returns:
            Dictionary mapping endpoint names to CSV file paths
        """
        logger.info("Starting full data export from Bubble...")
        start_time = datetime.now()
        
        exported_files = {}
        
        for endpoint_name, endpoint_path in config.BUBBLE_ENDPOINTS.items():
            try:
                csv_path = self.export_endpoint(endpoint_name, endpoint_path)
                if csv_path:
                    exported_files[endpoint_name] = csv_path
            except Exception as e:
                logger.error(f"Failed to export {endpoint_name}: {str(e)}")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Export completed in {duration:.2f} seconds")
        logger.info(f"Exported {len(exported_files)} endpoints")
        
        return exported_files


def main():
    """Main function to run export"""
    try:
        exporter = BubbleExporter()
        exported_files = exporter.export_all()
        
        print("\n=== Export Summary ===")
        for endpoint, filepath in exported_files.items():
            print(f"{endpoint}: {filepath}")
        
        return 0
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
