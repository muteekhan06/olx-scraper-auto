"""
Data Export Module.
Exports scraped data directly to TSV format.
"""

import csv
import json
import os
from datetime import date
from typing import Dict, List

from app.config import OUTPUT_CONFIG


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def get_ordered_columns(data: List[Dict]) -> List[str]:
    """
    Get columns in preferred order, excluding unwanted ones.
    
    Args:
        data: List of dictionaries with data
        
    Returns:
        Ordered list of column names
    """
    # Collect all keys
    all_keys: set = set()
    for row in data:
        all_keys.update(row.keys())
    
    # Remove excluded columns
    all_keys -= set(OUTPUT_CONFIG.EXCLUDED_COLUMNS)
    
    # Order columns
    ordered: List[str] = []
    
    # Add preferred columns first (in order)
    for col in OUTPUT_CONFIG.COLUMN_ORDER:
        if col in all_keys:
            ordered.append(col)
            all_keys.remove(col)
    
    # Add remaining columns alphabetically
    ordered.extend(sorted(all_keys))
    
    return ordered


def clean_record(record: Dict) -> Dict:
    """
    Clean a record by removing excluded columns and normalizing values.
    
    Args:
        record: Dictionary to clean
        
    Returns:
        Cleaned dictionary
    """
    clean: Dict = {}
    
    for k, v in record.items():
        # Skip excluded columns
        if k in OUTPUT_CONFIG.EXCLUDED_COLUMNS:
            continue
        
        # Skip error field
        if k == "error":
            continue
        
        # Normalize value
        if v is None:
            clean[k] = ""
        elif isinstance(v, list):
            clean[k] = ", ".join(str(x) for x in v)
        elif isinstance(v, str):
            # Clean whitespace and handle N/A
            v = v.strip()
            if v.upper() == "N/A":
                clean[k] = ""
            else:
                clean[k] = v
        else:
            clean[k] = str(v)
    
    return clean


def export_to_tsv(data: List[Dict], filename: str = None) -> str:
    """
    Export data to TSV file.
    
    Args:
        data: List of dictionaries to export
        filename: Optional custom filename (without extension)
        
    Returns:
        Path to the created TSV file
    """
    ensure_dir(OUTPUT_CONFIG.OUTPUT_DIR)
    
    if not filename:
        today = date.today().isoformat()
        filename = f"olx_lahore_{today}"
    
    filepath = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, f"{filename}.tsv")
    
    # Clean data
    cleaned_data = [clean_record(row) for row in data]
    
    # Get ordered columns
    columns = get_ordered_columns(cleaned_data)
    
    if not columns or not cleaned_data:
        return filepath
    
    # Write TSV
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        
        for row in cleaned_data:
            # Ensure all columns exist
            clean_row = {col: row.get(col, "") for col in columns}
            writer.writerow(clean_row)
    
    return filepath


def export_to_json(data: List[Dict], filename: str = None) -> str:
    """
    Export data to JSON file.
    
    Args:
        data: List of dictionaries to export
        filename: Optional custom filename (without extension)
        
    Returns:
        Path to the created JSON file
    """
    ensure_dir(OUTPUT_CONFIG.OUTPUT_DIR)
    
    if not filename:
        today = date.today().isoformat()
        filename = f"olx_lahore_{today}"
    
    filepath = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, f"{filename}.json")
    
    # Clean data
    cleaned_data = [clean_record(row) for row in data]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    return filepath
