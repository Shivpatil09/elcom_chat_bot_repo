import json
import re
from typing import Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rapidfuzz import fuzz, process

# Load the product catalog
with open("elcom_product_catalog_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

products = [p for p in data if p.get("product_name")]
FUZZY_MATCH_THRESHOLD = 65
MAX_RESULTS = 5

# --- Utility functions ---

def normalize(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()


def parse_numeric_range(text, unit):
    """
    Extracts numeric range like:
    - "between 100V and 300V"
    - "less than 5A"
    - "above 2 amps"
    Returns (min_val, max_val)
    """
    text = text.lower()
    numbers = [float(n) for n in
               re.findall(r"(\d+\.?\d*)", text)]

    if "between" in text and "and" in text and len(
            numbers) == 2:
        return (numbers[0], numbers[1])
    elif "less than" in text or "under" in text or "upto" in text:
        return (0, numbers[0])
    elif "more than" in text or "above" in text or "greater than" in text:
        return (numbers[0], float("inf"))
    elif len(numbers) == 1:
        return (numbers[0], numbers[0])
    return None


def extract_filters(query):
    filters = {}
    query_lower = query.lower()

    # Categorical filters
    if "spdt" in query_lower: filters[
        "description"] = "spdt"
    if "dpdt" in query_lower: filters[
        "description"] = "dpdt"
    if "rocker" in query_lower: filters[
        "description"] = "rocker"
    if "rotary" in query_lower: filters[
        "description"] = "rotary"
    if "panel" in query_lower: filters[
        "mounting_type"] = "panel"
    if "snap-in" in query_lower: filters[
        "mounting_type"] = "snap-in"
    if "chassis" in query_lower: filters[
        "mounting_type"] = "chassis"

    # Numeric filters
    voltage_range = parse_numeric_range(query_lower, "v")
    current_range = parse_numeric_range(query_lower, "a")

    if voltage_range:
        filters["voltage_range"] = voltage_range
    if current_range:
        filters["current_range"] = current_range

    return filters

def format_product_info(product):
    return (
        f"**{product.get('product_name', 'Unknown')}**\n"
        f"- Description: {product.get('description', 'N/A')}\n"
        f"- Rated Voltage: {product.get('rated_voltage', 'N/A')}\n"
        f"- Rated Current: {product.get('rated_current', 'N/A')}\n"
        f"- Compliance: {product.get('compliance', 'N/A')}\n"
        f"- Mounting Type: {product.get('mounting_type', 'N/A')}\n"
        f"- Temperature Range: {product.get('Operating Temperature ', 'N/A')}\n"
        f"- Reference Standard: {product.get('reference_standard', 'N/A')}\n"
        f"- Extra Features: {product.get('other_features') or 'Not specified'}\n"
    )

def format_multiple_products(products):
    response = f"I found {len(products)} product(s) that might match your query:\n\n"
    for i, product in enumerate(products, 1):
        response += f"**{i}.** {format_product_info(product)}\n"
    return response.strip()

# --- Core search logic ---

def search_by_product_name(query):
    query_normalized = normalize(query)
    for product in products:
        product_name_normalized = normalize(product.get("product_name", ""))
        if product_name_normalized == query_normalized or product_name_normalized in query_normalized:
            return product
    return None

def search_by_fuzzy_match(query):
    product_names = [normalize(p["product_name"]) for p in products]
    query_normalized = normalize(query)
    match, score, index = process.extractOne(query_normalized, product_names, scorer=fuzz.token_sort_ratio)
    if score > FUZZY_MATCH_THRESHOLD:
        return products[index]
    return None

def search_by_fields(query):
    query_words = normalize(query).split()
    filters = extract_filters(query)
    results = []

    for product in products:
        combined = normalize(" ".join([
            str(product.get("product_name", "")),
            str(product.get("description", "")),
            str(product.get("rated_voltage", "")),
            str(product.get("rated_current", "")),
            str(product.get("compliance", "")),
            str(product.get("mounting_type", ""))
        ]))

        match_score = sum(word in combined for word in query_words)

        # Check categorical filters
        passes_text_filters = all(
            filters[key] in str(product.get(key, "")).lower()
            for key in filters if key not in ["voltage_range", "current_range"]
        )

        # Check numeric filters
        passes_voltage = True
        if "voltage_range" in filters:
            try:
                product_voltage = float(re.findall(r"\d+", product.get("rated_voltage", ""))[0])
                vmin, vmax = filters["voltage_range"]
                passes_voltage = vmin <= product_voltage <= vmax
            except:
                passes_voltage = False

        passes_current = True
        if "current_range" in filters:
            try:
                product_current = float(re.findall(r"\d+", product.get("rated_current", ""))[0])
                cmin, cmax = filters["current_range"]
                passes_current = cmin <= product_current <= cmax
            except:
                passes_current = False

        if match_score and passes_text_filters and passes_voltage and passes_current:
            results.append((match_score, product))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results[:MAX_RESULTS]]


def handle_query(query):
    # First try to find a strong product name match
    result = search_by_product_name(query)
    if result:
        return f"Here are the specs for the product you asked about:\n\n{result}"

    # No exact match → apply all relevant filters
    matches = search_by_fields(query)
    if not matches:
        return (
            "Hmm... I couldn’t find anything that matches your request. "
            "Try specifying a product name or key feature like voltage/current/mounting type.\n\n"
            "Example queries:\n"
            "- 'RS-1601 switch'\n"
            "- '16A rocker switch, panel mount, 250V'\n"
            "- 'SPDT switch under 6A'"
        )

    if len(matches) == 1:
        return f"Here's a match based on your filters:\n\n{format_product_info(matches[0])}"

    # Multiple relevant matches
    response = f"I found {len(matches)} product(s) that might match your query:\n\n"
    for i, product in enumerate(matches, 1):
        response += f"**{i}.** {format_product_info(product)}\n"
    return response.strip()


# --- Rasa Action ---

class ActionSearchProduct(Action):
    def name(self) -> str:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        intent = tracker.latest_message.get("intent",
                                            {}).get("name")
        if intent not in ["product_search",
                          "ask_product_details"]:
            dispatcher.utter_message(
                text="Hmm, I’m not sure what you meant. Could you rephrase?")
            return []

        user_query = tracker.latest_message.get("text")
        response = handle_query(user_query)
        dispatcher.utter_message(text=response)
        return []

