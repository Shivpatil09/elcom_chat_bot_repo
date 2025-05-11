import json
import re
import logging
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rapidfuzz import fuzz, process
from difflib import get_close_matches

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common words to remove from queries
STOP_WORDS = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}

# Product attribute synonyms
ATTRIBUTE_SYNONYMS = {
    "voltage": ["v", "volt", "volts", "voltage", "rated voltage"],
    "current": ["a", "amp", "amps", "ampere", "amperes", "current", "rated current"],
    "switch": ["switches", "switching", "spst", "spdt", "dpst", "dpdt"],
    "rocker": ["rocker", "toggle", "lever"],
    "rotary": ["rotary", "rotating", "knob"],
    "panel": ["panel", "surface", "mount"],
    "mount": ["mount", "mounting", "installed", "snap-in", "chassis"],
    "temperature": ["temp", "temperature", "operating temperature"],
    "compliance": ["standard", "compliance", "certification", "certified"],
    "function": ["function", "operation", "mode", "state"]
}

# Product categories with common misspellings
PRODUCT_CATEGORIES = {
    "switch": ["switch", "switches", "toggle", "rocker", "rotary", "push button", "spst", "spdt", "dpst", "dpdt"],
    "ev_connector": ["ev connector", "electric vehicle connector", "charging connector", "ev charging", "ev conector", "ev conectors", "ev conector", "ev conectors"],
    "industrial_connector": ["industrial connector", "industrial plug", "industrial socket", "ip44", "ip67", "industrial conector", "industrial conectors"],
    "solar_connector": ["solar connector", "pv connector", "solar panel connector", "y connector", "solar conector", "solar conectors"],
    "nema_connector": ["nema connector", "nema plug", "nema socket", "twist lock", "nema conector", "nema conectors"],
    "relay": ["relay", "contactor", "solid state relay"],
    "sensor": ["sensor", "proximity", "limit", "photoelectric", "motion sensor"],
    "accessory": ["accessory", "mount", "bracket", "cover", "adapter", "holder", "fuse holder"],
    "filter": ["filter", "emi filter", "rfi filter", "power filter"],
    "pdu": ["pdu", "power distribution unit", "power strip", "power distribution"],
    "breaker": ["breaker", "circuit breaker", "fuse", "protection"],
    "indicator": ["indicator", "light", "led", "display", "meter"],
    "power": ["power supply", "power cord", "power cable", "power adapter"],
    "terminal": ["terminal block", "terminal strip", "terminal connector"],
    "control": ["control", "controller", "switch", "button", "key"]
}

# Constants
FUZZY_MATCH_THRESHOLD = 65
MAX_RESULTS = 5
MIN_RELEVANCE_SCORE = 0.3

def normalize(text: str) -> str:
    """Enhanced text normalization with special character handling."""
    # Remove special characters but keep spaces and numbers
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Load the product catalog
with open("elcom_product_catalog_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Initialize search history
search_history = defaultdict(int)
popular_products = []

# Create a combined search field for each product and categorize
for product in data:
    product["search_field"] = f"{product.get('product_name', '')} {product.get('description', '')}".strip()
    # Add category based on description
    product["category"] = "other"
    for category, keywords in PRODUCT_CATEGORIES.items():
        if any(keyword in normalize(product.get("description", "")) for keyword in keywords):
            product["category"] = category
            break

products = [p for p in data if p.get("product_name")]

# --- Utility functions ---

def update_search_history(product_id: str):
    """Update search history and popular products."""
    search_history[product_id] += 1
    # Update popular products list
    global popular_products
    popular_products = sorted(search_history.items(), key=lambda x: x[1], reverse=True)[:5]

def get_popular_products() -> List[Dict[str, Any]]:
    """Get the most popular products based on search history."""
    return [p for p in products if p["product_name"] in [pid for pid, _ in popular_products]]

def correct_spelling(word: str, word_list: List[str], cutoff: float = 0.8) -> str:
    """Correct spelling using fuzzy matching."""
    matches = get_close_matches(word, word_list, n=1, cutoff=cutoff)
    return matches[0] if matches else word

def preprocess_query(query: str) -> Tuple[str, Dict[str, Any]]:
    """Enhanced query preprocessing with spelling correction."""
    try:
        query = normalize(query)
        words = query.split()
        
        # Remove stop words
        words = [w for w in words if w not in STOP_WORDS]
        
        # Extract attributes and category
        attributes = {}
        category = None
        
        # Create a list of all possible category keywords
        all_category_keywords = []
        for keywords in PRODUCT_CATEGORIES.values():
            all_category_keywords.extend(keywords)
        
        # Correct spelling in the query
        corrected_words = []
        for word in words:
            corrected_word = correct_spelling(word, all_category_keywords)
            corrected_words.append(corrected_word)
        
        # Join corrected words back into query
        corrected_query = " ".join(corrected_words)
        
        # Check for specific connector types first
        if "ev" in corrected_query.lower() or "electric vehicle" in corrected_query.lower():
            category = "ev_connector"
        elif "industrial" in corrected_query.lower():
            category = "industrial_connector"
        elif "solar" in corrected_query.lower() or "pv" in corrected_query.lower():
            category = "solar_connector"
        elif "nema" in corrected_query.lower():
            category = "nema_connector"
        else:
            # Check other categories with corrected words
            for word in corrected_words:
                for cat, keywords in PRODUCT_CATEGORIES.items():
                    if word in keywords:
                        category = cat
                        break
                if category:
                    break
        
        # Check for attributes with corrected words
        for word in corrected_words:
            for attr, synonyms in ATTRIBUTE_SYNONYMS.items():
                if word in synonyms:
                    attributes[attr] = True
        
        # Extract numeric values with units
        voltage_matches = re.findall(r"(\d+)\s*(?:v|volt|volts|voltage)", corrected_query)
        current_matches = re.findall(r"(\d+)\s*(?:a|amp|amps|ampere|amperes|current)", corrected_query)
        
        if voltage_matches:
            attributes["voltage_value"] = float(voltage_matches[0])
        if current_matches:
            attributes["current_value"] = float(current_matches[0])
        
        if category:
            attributes["category"] = category
        
        return corrected_query, attributes
    except Exception as e:
        logger.error(f"Error preprocessing query: {str(e)}")
        return query, {}

def calculate_relevance_score(product: Dict[str, Any], query: str, attributes: Dict[str, Any]) -> float:
    """Enhanced relevance scoring with optimized weights."""
    try:
        score = 0.0
        query = query.lower()
        product_name = normalize(product.get("product_name", ""))
        description = normalize(product.get("description", ""))
        
        # 1. Category Match (Highest Priority)
        if "category" in attributes:
            if attributes["category"] == "ev_connector" and "ev" in description:
                score += 3.0
            elif attributes["category"] == product.get("category"):
                score += 2.0
        
        # 2. Exact Product Name Match (High Priority)
        if query in product_name:
            score += 2.5
        
        # 3. Product Name Contains Query (High Priority)
        elif query in product_name:
            score += 2.0
        
        # 4. Description Match (Medium Priority)
        if query in description:
            score += 1.5
        
        # 5. Fuzzy Match in Search Field (Medium Priority)
        search_field = normalize(product.get("search_field", ""))
        fuzzy_score = fuzz.token_sort_ratio(query, search_field) / 100
        score += fuzzy_score * 1.0
        
        # 6. Technical Specifications (High Priority)
        for attr, value in attributes.items():
            if attr == "voltage_value":
                try:
                    product_voltage = float(re.findall(r"\d+", product.get("rated_voltage", "0"))[0])
                    if abs(product_voltage - value) < 10:  # Within 10V
                        score += 1.0
                    elif abs(product_voltage - value) < 50:  # Within 50V
                        score += 0.5
                except:
                    pass
            elif attr == "current_value":
                try:
                    current_str = product.get("rated_current", "")
                    current_values = [float(re.findall(r"\d+", c)[0]) for c in current_str.split(",")]
                    if any(abs(c - value) < 1 for c in current_values):  # Within 1A
                        score += 1.0
                    elif any(abs(c - value) < 5 for c in current_values):  # Within 5A
                        score += 0.5
                except:
                    pass
        
        # 7. Feature/Type Matches (Medium Priority)
        if product.get("other_features"):
            for feature_list in product["other_features"].values():
                if isinstance(feature_list, list):
                    if any(query in normalize(str(f)) for f in feature_list):
                        score += 0.8
        
        # 8. Compliance Match (Low Priority)
        if product.get("compliance"):
            compliance_standards = product["compliance"].get("standards", [])
            if any(query in normalize(str(s)) for s in compliance_standards):
                score += 0.3
        
        return score
    except Exception as e:
        logger.error(f"Error calculating relevance score: {str(e)}")
        return 0.0

def search_products(query: str) -> List[Dict[str, Any]]:
    """Enhanced product search with error handling."""
    try:
        processed_query, attributes = preprocess_query(query)
        
        # If searching for EV connectors, prioritize EV-related products
        if "ev" in processed_query.lower():
            attributes["category"] = "ev_connector"
        
        results = []
        for product in products:
            score = calculate_relevance_score(product, processed_query, attributes)
            if score > MIN_RELEVANCE_SCORE:
                results.append((score, product))
        
        # Sort by score and category match
        results.sort(key=lambda x: (x[0], x[1].get("category") == attributes.get("category")), reverse=True)
        return [p for _, p in results[:MAX_RESULTS]]
    except Exception as e:
        logger.error(f"Error in search_products: {str(e)}")
        return []

def format_product_info(product: Dict[str, Any], query: str = "") -> str:
    """Format product information to match the exact design shown."""
    try:
        sections = []
        
        # Product Name at the top
        sections.append(f"{product.get('product_name')}:")
        sections.append("")
        
        # Product Description
        sections.append("### Product Description")
        sections.append(product.get('description', 'N/A'))
        sections.append("")
        
        # Technical Specifications
        sections.append("### Technical Specifications")
        sections.append(f"• Rated Voltage: {product.get('rated_voltage', 'N/A')}")
        
        current = product.get('rated_current', 'N/A')
        if isinstance(current, str):
            current = current.replace(" / ", "/")
        sections.append(f"• Rated Current: {current}")
        
        mounting = product.get('mounting_type', 'N/A')
        sections.append(f"• Mounting Type: {mounting}")
        
        temp_range = product.get('operating_temperature', 'N/A')
        sections.append(f"• Temperature Range: {temp_range}")
        sections.append("")
        
        # Standards & Compliance
        sections.append("### Standards & Compliance")
        if product.get('compliance'):
            standards = product['compliance'].get('standards', [])
            if standards and standards != ['NaN']:
                processed_standards = []
                for std in standards:
                    std_str = str(std).strip()
                    if std_str.lower() != 'nan':
                        std_str = std_str.replace("( On Request )", "").strip()
                        processed_standards.append(std_str)
                
                if processed_standards:
                    sections.append(f"• Standards: {', '.join(processed_standards)}")
        
        if product.get('reference_standard'):
            ref_standards = str(product.get('reference_standard')).split(',')
            ref_standards = [std.strip() for std in ref_standards]
            sections.append(f"• Reference Standards: {', '.join(ref_standards)}")
        sections.append("")
        
        # Additional Features
        if product.get('other_features'):
            sections.append("### Additional Features")
            for key, value in product['other_features'].items():
                if isinstance(value, list) and value:
                    value_str = []
                    for item in value:
                        item_str = str(item).strip("[]'\"")
                        if item_str and item_str.lower() != 'nan':
                            item_str = item_str.replace(" : ", ": ")
                            value_str.append(item_str)
                    if value_str:
                        sections.append(f"• {key}: {', '.join(value_str)}")
        
        return "\n".join(sections).strip()
    except Exception as e:
        logger.error(f"Error formatting product info: {str(e)}")
        return f"Error displaying product information for {product.get('product_name', 'Unknown')}"

def format_multiple_products(products: List[Dict[str, Any]]) -> str:
    """Format multiple products for display."""
    return "\n\n---\n\n".join(format_product_info(p) for p in products)

def parse_numeric_range(query: str, unit: str) -> Optional[Tuple[float, float]]:
    """Parse numeric range from query string for a given unit."""
    pattern = rf"(\d+)\s*{unit}\s*to\s*(\d+)\s*{unit}"
    match = re.search(pattern, query)
    if match:
        return (float(match.group(1)), float(match.group(2)))
    return None

def extract_filters(query: str) -> Dict[str, Any]:
    """Extract filters from the query string."""
    filters = {}
    query_lower = query.lower()

    # Categorical filters
    if "spdt" in query_lower: filters["description"] = "spdt"
    if "dpdt" in query_lower: filters["description"] = "dpdt"
    if "rocker" in query_lower: filters["description"] = "rocker"
    if "rotary" in query_lower: filters["description"] = "rotary"
    if "panel" in query_lower: filters["mounting_type"] = "panel"
    if "snap-in" in query_lower: filters["mounting_type"] = "snap-in"
    if "chassis" in query_lower: filters["mounting_type"] = "chassis"

    # Numeric filters
    voltage_range = parse_numeric_range(query_lower, "v")
    current_range = parse_numeric_range(query_lower, "a")

    if voltage_range:
        filters["voltage_range"] = voltage_range
    if current_range:
        filters["current_range"] = current_range

    return filters

# --- Rasa Action ---

class ActionSearchProduct(Action):
    def name(self) -> str:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            intent = tracker.latest_message.get("intent", {}).get("name")
            
            if intent not in ["product_search", "ask_product_details", "ask_product_info"]:
                dispatcher.utter_message(
                    text="Hmm, I'm not sure what you meant. Could you rephrase?")
                return []

            user_query = tracker.latest_message.get("text")
            
            results = search_products(user_query)
            if not results:
                response = (
                    "I couldn't find any products matching your query. "
                    "Try being more specific with product names or key features like:\n"
                    "- Voltage rating (e.g., '250V')\n"
                    "- Current rating (e.g., '16A')\n"
                    "- Mounting type (e.g., 'panel mount')\n"
                    "- Protection degree (e.g., 'IP67')\n"
                )
            else:
                # Format the results
                if len(results) == 1:
                    response = format_product_info(results[0], user_query)
                else:
                    # Add introduction with count information
                    formatted_results = []
                    for product in results:
                        formatted_results.append(format_product_info(product, user_query))
                    response = "\n\n---\n\n".join(formatted_results)
        
            dispatcher.utter_message(text=response)
            
            if results:
                update_search_history(results[0]['product_name'])
            
            return []
        except Exception as e:
            logger.error(f"Error in ActionSearchProduct: {str(e)}")
            dispatcher.utter_message(
                text="Sorry, I encountered an error while processing your query. Please try again.")
            return []

