import json
import os

def count_products(catalog_file: str) -> int:
    """Count the number of products in the catalog file."""
    try:
        # Get the absolute path of the catalog file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, catalog_file)
        
        # Read and count products
        with open(file_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            return len(catalog)
    except Exception as e:
        print(f"Error counting products: {str(e)}")
        return 0

if __name__ == "__main__":
    catalog_file = "elcom_product_catalog_cleaned.json"
    count = count_products(catalog_file)
    print(f"Number of products in {catalog_file}: {count}") 