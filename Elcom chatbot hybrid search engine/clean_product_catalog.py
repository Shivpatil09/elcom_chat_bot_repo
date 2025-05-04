import json
import re
import pandas as pd
from typing import Dict, Any, List
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def standardize_field_names(product: Dict[str, Any]) -> Dict[str, Any]:
    """Convert field names to lowercase with underscores."""
    field_mapping = {
        "Product Name": "product_name",
        "Description": "description",
        "Rated Voltage": "rated_voltage",
        "Rated Current": "rated_current",
        "Compliance": "compliance",
        "Mounting Type": "mounting_type",
        "Operating Temperature ": "operating_temperature",
        "Reference Standard": "reference_standard",
        "Other Features": "other_features"
    }
    
    standardized = {}
    for old_key, new_key in field_mapping.items():
        if old_key in product:
            standardized[new_key] = product[old_key]
    return standardized

def standardize_rated_current(current_str: Any) -> str:
    """Standardize the format of rated current values."""
    try:
        # Convert to string if it's a number
        if isinstance(current_str, (int, float)):
            current_str = str(current_str)
        
        # Handle None or empty values
        if not current_str:
            return "N/A"
            
        # Remove spaces and convert to uppercase
        current_str = str(current_str).replace(" ", "").upper()
        
        # Handle different formats
        if "/" in current_str:
            # Split by slash and join with comma
            currents = current_str.split("/")
            return ", ".join(currents)
        elif "," in current_str:
            # Already comma-separated, just clean up
            currents = [c.strip() for c in current_str.split(",")]
            return ", ".join(currents)
        else:
            return current_str
    except Exception as e:
        print(f"Error processing current value: {current_str}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return "N/A"

def standardize_compliance(compliance_str: Any) -> Dict[str, Any]:
    """Standardize compliance information."""
    try:
        # Handle None or empty values
        if not compliance_str:
            return {"standards": [], "on_request": False}
            
        # Convert to string if it's not already
        compliance_str = str(compliance_str)
        
        # Remove "On Request" text
        compliance_str = compliance_str.replace("( On Request )", "").strip()
        
        # Split by comma and clean up
        standards = [s.strip() for s in compliance_str.split(",")]
        
        return {
            "standards": standards,
            "on_request": "( On Request )" in str(compliance_str)
        }
    except Exception as e:
        print(f"Error processing compliance: {compliance_str}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return {"standards": [], "on_request": False}

def standardize_other_features(features: Any) -> Dict[str, List[str]]:
    """Standardize the structure of other features while preserving all original categories."""
    try:
        # Handle None or empty values
        if not features:
            return {}
            
        # Ensure features is a dictionary
        if not isinstance(features, dict):
            return {"additional": [str(features)]}
            
        standardized = {}
        
        for key, values in features.items():
            # Clean the key name
            key = str(key).strip()
            key = re.sub(r'\s+', ' ', key)
            
            # Ensure values is a list
            if not isinstance(values, list):
                values = [str(values)]
            
            # Clean each value
            cleaned_values = []
            for value in values:
                if pd.isna(value):
                    continue
                value = str(value).strip()
                value = re.sub(r'\s+', ' ', value)
                cleaned_values.append(value)
            
            if cleaned_values:
                standardized[key] = cleaned_values
        
        return standardized
    except Exception as e:
        print(f"Error processing other features: {features}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return {}

def clean_voltage(voltage: str) -> str:
    """Clean and standardize voltage values."""
    if pd.isna(voltage):
        return "N/A"
    
    # Remove extra spaces and standardize units
    voltage = str(voltage).strip().upper()
    voltage = re.sub(r'\s+', ' ', voltage)
    
    # Standardize voltage format
    voltage = re.sub(r'V(?:OLT)?S?', 'V', voltage)
    voltage = re.sub(r'AC/DC', 'AC/DC', voltage)
    
    return voltage

def clean_current(current: str) -> str:
    """Clean and standardize current values."""
    if pd.isna(current):
        return "N/A"
    
    # Remove extra spaces and standardize units
    current = str(current).strip().upper()
    current = re.sub(r'\s+', ' ', current)
    
    # Standardize current format
    current = re.sub(r'A(?:MP)?S?', 'A', current)
    current = re.sub(r'MAX\.?', 'MAX.', current)
    
    return current

def clean_compliance(compliance: Any) -> Dict[str, Any]:
    """Clean and standardize compliance information."""
    if pd.isna(compliance):
        return {"standards": ["N/A"], "on_request": False}
    
    if isinstance(compliance, str):
        standards = [s.strip() for s in compliance.split(',')]
        return {"standards": standards, "on_request": False}
    
    if isinstance(compliance, dict):
        standards = compliance.get("standards", [])
        if isinstance(standards, str):
            standards = [s.strip() for s in standards.split(',')]
        return {
            "standards": standards,
            "on_request": compliance.get("on_request", False)
        }
    
    return {"standards": ["N/A"], "on_request": False}

def clean_features(features: Any) -> Dict[str, List[str]]:
    """Clean and standardize product features while preserving all categories and their values."""
    try:
        if pd.isna(features):
            return {}
        
        if isinstance(features, dict):
            cleaned_features = {}
            for category, items in features.items():
                if pd.isna(items):
                    continue
                    
                # Clean the category name
                category = str(category).strip()
                category = re.sub(r'\s+', ' ', category)
                
                if isinstance(items, list):
                    # Clean each item in the list
                    cleaned_items = []
                    for item in items:
                        if pd.isna(item):
                            continue
                        # Clean and standardize the item
                        item = str(item).strip()
                        item = re.sub(r'\s+', ' ', item)
                        cleaned_items.append(item)
                    
                    if cleaned_items:
                        cleaned_features[category] = cleaned_items
                else:
                    # Handle single items
                    item = str(items).strip()
                    item = re.sub(r'\s+', ' ', item)
                    cleaned_features[category] = [item]
            
            # Special handling for EV connectors
            if any(key.lower() in ['type', 'protection degree', 'durability'] for key in cleaned_features.keys()):
                # Ensure all EV-specific features are properly categorized
                ev_features = {}
                for key, value in cleaned_features.items():
                    key_lower = key.lower()
                    if 'type' in key_lower:
                        ev_features['Type'] = value
                    elif 'protection' in key_lower or 'ip' in key_lower:
                        ev_features['Protection Degree'] = value
                    elif 'durability' in key_lower:
                        if 'electrical' in key_lower:
                            ev_features['Durability (Electrical Cycles Max.)'] = value
                        elif 'mechanical' in key_lower or 'mechinal' in key_lower:
                            ev_features['Durability (Mechanical Cycles Max.)'] = value
                    else:
                        ev_features[key] = value
                return ev_features
            
            return cleaned_features
        
        # If features is not a dict, try to convert it
        if isinstance(features, (str, int, float)):
            return {"additional": [str(features).strip()]}
        
        return {}
    except Exception as e:
        logger.error(f"Error cleaning features: {str(e)}")
        return {}

def clean_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and standardize a single product entry."""
    try:
        # Basic validation
        if not product or not isinstance(product, dict):
            logger.warning("Invalid product data")
            return None
            
        # Get product name first for logging
        product_name = product.get("Product Name", "Unknown")
        if not product_name or product_name == "Unknown":
            logger.warning("Product missing name")
            return None
            
        # Clean each field with fallback to original value
        cleaned = {
            "product_name": str(product_name).strip(),
            "description": str(product.get("Description", "N/A")).strip(),
            "rated_voltage": clean_voltage(product.get("Rated Voltage")),
            "rated_current": clean_current(product.get("Rated Current")),
            "compliance": clean_compliance(product.get("Compliance")),
            "mounting_type": str(product.get("Mounting Type", "N/A")).strip(),
            "operating_temperature": str(product.get("Operating Temperature", "N/A")).strip(),
            "reference_standard": str(product.get("Reference Standard", "N/A")).strip(),
            "other_features": standardize_other_features(product.get("Other Features", {}))
        }
        
        # Create a search field for better matching
        cleaned["search_field"] = f"{cleaned['product_name']} {cleaned['description']}".strip()
        
        # Validate required fields
        if not cleaned["product_name"] or cleaned["product_name"] == "N/A":
            logger.warning(f"Product {product_name} has invalid name")
            return None
            
        if not cleaned["description"] or cleaned["description"] == "N/A":
            logger.warning(f"Product {product_name} has invalid description")
            return None
            
        # Special handling for EV connectors
        if "EV" in cleaned["description"].upper() or "ELECTRIC VEHICLE" in cleaned["description"].upper():
            # Ensure operating temperature is preserved
            if cleaned["operating_temperature"] == "N/A":
                cleaned["operating_temperature"] = "-30°C To 50°"
            
            # Ensure compliance is properly structured
            if cleaned["compliance"]["standards"] == ["N/A"]:
                cleaned["compliance"] = {"standards": [], "on_request": False}
            
            # Ensure mounting type is preserved
            if cleaned["mounting_type"] == "N/A":
                cleaned["mounting_type"] = "Panel Mount"
            
        return cleaned
    except Exception as e:
        logger.error(f"Error cleaning product {product.get('Product Name', 'Unknown')}: {str(e)}")
        # Instead of returning None, return the original product with basic cleaning
        try:
            return {
                "product_name": str(product.get("Product Name", "N/A")).strip(),
                "description": str(product.get("Description", "N/A")).strip(),
                "rated_voltage": str(product.get("Rated Voltage", "N/A")).strip(),
                "rated_current": str(product.get("Rated Current", "N/A")).strip(),
                "compliance": {"standards": [], "on_request": False},
                "mounting_type": str(product.get("Mounting Type", "N/A")).strip(),
                "operating_temperature": str(product.get("Operating Temperature", "N/A")).strip(),
                "reference_standard": str(product.get("Reference Standard", "N/A")).strip(),
                "other_features": standardize_other_features(product.get("Other Features", {})),
                "search_field": f"{product.get('Product Name', 'N/A')} {product.get('Description', 'N/A')}".strip()
            }
        except:
            return None

def clean_catalog(input_file: str, output_file: str):
    """Clean the entire product catalog."""
    try:
        # Read the input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        if not isinstance(catalog, list):
            logger.error("Input catalog is not a list")
            return False
            
        total_products = len(catalog)
        logger.info(f"Processing {total_products} products")
        
        # Clean each product
        cleaned_products = []
        skipped_products = []
        
        for i, product in enumerate(catalog, 1):
            try:
                cleaned = clean_product(product)
                if cleaned:
                    cleaned_products.append(cleaned)
                else:
                    skipped_products.append(product.get("Product Name", f"Product {i}"))
            except Exception as e:
                logger.error(f"Error processing product {i}: {str(e)}")
                skipped_products.append(product.get("Product Name", f"Product {i}"))
            
            if i % 100 == 0:
                logger.info(f"Processed {i}/{total_products} products")
        
        # Log statistics
        logger.info(f"Successfully cleaned {len(cleaned_products)} products")
        if skipped_products:
            logger.warning(f"Skipped {len(skipped_products)} products: {', '.join(skipped_products[:10])}...")
        
        # Write the cleaned catalog to a new JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_products, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning catalog: {str(e)}")
        return False

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output file paths relative to the script directory
    input_file = os.path.join(script_dir, "elcom_product_catalog_formatted_f1_copy.json")
    output_file = os.path.join(script_dir, "elcom_product_catalog_cleaned.json")
    
    print("Cleaning product catalog...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    if clean_catalog(input_file, output_file):
        logger.info("Catalog cleaning completed successfully")
    else:
        logger.error("Catalog cleaning failed") 