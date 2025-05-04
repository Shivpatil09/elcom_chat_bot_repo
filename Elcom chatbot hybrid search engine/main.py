import json
from rapidfuzz import fuzz, process
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurable thresholds
FUZZY_MATCH_THRESHOLD = 60  # Lowered to improve partial match success
MIN_RELEVANCE_SCORE = 0.3  # Minimum score for a result to be considered relevant
MAX_RESULTS = 5

# Load product data from JSON
with open("elcom_product_catalog_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Clean null entries
products = [p for p in data if p.get("product_name")]

# Common misspellings and variations
SPELLING_VARIATIONS = {
    "connector": ["conector", "conecter", "connecter"],
    "industrial": ["industrail", "industriel"],
    "voltage": ["volt", "volts"],
    "current": ["amp", "amps", "ampere"],
    "panel": ["pannel"],
    "mount": ["mounted", "mounting"],
    "solar": ["soler", "solr"],
    "electric": ["electic", "elektric"],
    "vehicle": ["vehical", "vehicel"],
    "nema": ["nema", "nema"],
    "twist": ["twisted", "twisting"],
    "lock": ["locked", "locking"]
}

def normalize(text: str) -> str:
    """Enhanced text normalization with spelling correction."""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase and remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()
    
    # Replace common misspellings
    words = text.split()
    corrected_words = []
    for word in words:
        # Check for spelling variations
        for correct, variations in SPELLING_VARIATIONS.items():
            if word in variations:
                word = correct
                break
        corrected_words.append(word)
    
    return " ".join(corrected_words)

def extract_filters(query: str) -> Dict[str, str]:
    """Extract filters from the query with improved pattern matching."""
    filters = {}
    query = query.lower()
    
    # Voltage patterns
    voltage_patterns = [
        (r"(\d+)\s*v(?:olt)?s?", "rated_voltage"),
        (r"(\d+)\s*v(?:olt)?s?\s*ac", "rated_voltage"),
        (r"(\d+)\s*v(?:olt)?s?\s*dc", "rated_voltage")
    ]
    
    # Current patterns
    current_patterns = [
        (r"(\d+)\s*a(?:mp)?s?", "rated_current"),
        (r"(\d+)\s*a(?:mp)?s?\s*ac", "rated_current"),
        (r"(\d+)\s*a(?:mp)?s?\s*dc", "rated_current")
    ]
    
    # Mounting type patterns
    mounting_patterns = [
        (r"panel\s*mount", "mounting_type"),
        (r"chassis\s*mount", "mounting_type"),
        (r"pcb\s*mount", "mounting_type"),
        (r"screw\s*mount", "mounting_type")
    ]
    
    # IP rating patterns
    ip_patterns = [
        (r"ip\s*(\d+)", "other_features"),
        (r"protection\s*degree\s*ip\s*(\d+)", "other_features")
    ]
    
    # Combine all patterns
    all_patterns = voltage_patterns + current_patterns + mounting_patterns + ip_patterns
    
    for pattern, field in all_patterns:
        matches = re.finditer(pattern, query)
        for match in matches:
            value = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if field not in filters:
                filters[field] = value
    
    return filters

def calculate_relevance_score(product: Dict[str, Any], query: str, filters: Dict[str, str]) -> float:
    """Enhanced relevance scoring with multiple factors."""
    try:
        score = 0.0
        query = normalize(query)
        
        # Get normalized product fields
        product_name = normalize(product.get("product_name", ""))
        description = normalize(product.get("description", ""))
        search_field = normalize(product.get("search_field", ""))
        
        # 1. Exact matches (highest priority)
        if query in product_name:
            score += 3.0
        if query in description:
            score += 2.0
        
        # 2. Fuzzy matches
        name_score = fuzz.token_sort_ratio(query, product_name) / 100
        desc_score = fuzz.token_sort_ratio(query, description) / 100
        search_score = fuzz.token_sort_ratio(query, search_field) / 100
        
        score += name_score * 2.0 + desc_score * 1.5 + search_score * 1.0
        
        # 3. Filter matches
        for field, value in filters.items():
            if field in product:
                if isinstance(product[field], str):
                    if value.lower() in product[field].lower():
                        score += 1.5
                elif isinstance(product[field], dict):
                    if any(value.lower() in str(v).lower() for v in product[field].values()):
                        score += 1.5
                elif isinstance(product[field], list):
                    if any(value.lower() in str(v).lower() for v in product[field]):
                        score += 1.5
        
        return score
    except Exception as e:
        logger.error(f"Error calculating relevance score: {str(e)}")
        return 0.0

def search_by_fields(query: str) -> List[Dict[str, Any]]:
    """Enhanced search across multiple fields with improved filtering."""
    try:
        query = normalize(query)
        filters = extract_filters(query)
        results = []
        
        for product in products:
            score = calculate_relevance_score(product, query, filters)
            if score >= MIN_RELEVANCE_SCORE:
                results.append((score, product))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results[:MAX_RESULTS]]
    except Exception as e:
        logger.error(f"Error in search_by_fields: {str(e)}")
        return []

def handle_query(query: str) -> str:
    """Enhanced query handling with improved error handling and results formatting."""
    try:
        if not query or not isinstance(query, str):
            return "Please provide a valid search query."
        
        results = search_by_fields(query)
        
        if not results:
            return (
                "I couldn't find any products matching your query. "
                "Try being more specific with product names or key features like:\n"
                "- Voltage rating (e.g., '250V')\n"
                "- Current rating (e.g., '16A')\n"
                "- Mounting type (e.g., 'panel mount')\n"
                "- Protection degree (e.g., 'IP67')\n"
            )
        
        # Format the results in a consistent way
        if len(results) == 1:
            return f"Sure! Here's what I found about **{results[0]['product_name']}**: " + format_product_info(results[0], query)
        
        # For multiple results, format each one with a separator
        formatted_results = []
        for product in results:
            formatted_results.append(
                f"Sure! Here's what I found about **{product['product_name']}**: " + 
                format_product_info(product, query)
            )
        return "\n\n---\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error handling query: {str(e)}")
        return "Sorry, I encountered an error while processing your query. Please try again."

# Highlight query terms in text
def highlight_matches(text, query):
    for word in query.lower().split():
        text = re.sub(fr"\b({re.escape(word)})\b", r"**\1**", text, flags=re.IGNORECASE)
    return text

# Format product response conversationally
def format_product_info(product, query=None):
    response = (
        f"Sure! Here's what I found about **{product['product_name']}**:\n"
        f"- It's described as: {product['description']}\n"
        f"- Rated Voltage: {product['rated_voltage']}\n"
        f"- Rated Current: {product['rated_current']}\n"
        f"- Compliance: {product['compliance']}\n"
        f"- Mounting Type: {product['mounting_type']}\n"
        f"- Temperature Range: {product.get('Operating Temperature ', 'N/A')}\n"
        f"- Reference Standard: {product['reference_standard']}\n"
        f"- Extra Features: {product['other_features'] or 'Not specified'}\n"
    )
    return highlight_matches(response, query) if query else response

# CLI with loop
def main():
    print("Hi there! I'm your Elcom product assistant. Ask me anything about our switches, filters, or components. Type 'exit' to end the chat.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: It was great helping you. Have a wonderful day!")
            break
        response = handle_query(user_input)
        print("\nBot: " + response + "\n")

if __name__ == "__main__":
    main()
