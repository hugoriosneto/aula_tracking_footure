#!/usr/bin/env python
"""
Download sample data for PFF FC tracking visualization.

This script downloads sample PFF FC tracking data files
to use with the visualization notebooks. It downloads files
from the kloppy test fixtures when available.
"""

import os
import sys
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URLs for kloppy test files
KLOPPY_BASE_URL = "https://raw.githubusercontent.com/PySport/kloppy/master/kloppy/tests/files/"

# Files to download
PFF_FILES = [
    "pff_metadata_10517.json",
    "pff_rosters_10517.json", 
    "pff_10517.jsonl.bz2"
]

def download_file(url, destination):
    """Download a file from URL to destination."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        logger.info(f"Downloading {url} ({total_size/1024:.1f} KB)")
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Successfully downloaded to {destination}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return False

def main():
    """Main function to download all required files."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    logger.info("Starting download of PFF FC sample data")
    
    success = True
    for filename in PFF_FILES:
        url = f"{KLOPPY_BASE_URL}{filename}"
        dest_path = data_dir / filename
        
        if dest_path.exists():
            logger.info(f"File {dest_path} already exists, skipping")
            continue
            
        if not download_file(url, dest_path):
            success = False
    
    if success:
        logger.info("All files downloaded successfully!")
        logger.info("You can now run the visualization notebooks.")
    else:
        logger.error("Some files could not be downloaded. Please check the logs.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 