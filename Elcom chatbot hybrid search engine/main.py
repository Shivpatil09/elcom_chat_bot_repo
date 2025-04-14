import json
from rapidfuzz import fuzz, process
import re

# Configurable threshold
FUZZY_MATCH_THRESHOLD = 65  # Lowered to improve partial match success
MAX_RESULTS = 5

# Load product data from JSON
with open("elcom_product_catalog_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Clean null entries
products = [p for p in data if p.get("product_name")]

# Normalize text for comparison
def normalize(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()

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

# Extract filters from query
def extract_filters(query):
    filters = {}
    query_lower = query.lower()
    if "spdt" in query_lower:
        filters["description"] = "spdt"
    if "dpdt" in query_lower:
        filters["description"] = "dpdt"
    if "rocker" in query_lower:
        filters["description"] = "rocker"
    if "rotary" in query_lower:
        filters["description"] = "rotary"
    if "panel" in query_lower:
        filters["mounting_type"] = "panel"
    if "snap-in" in query_lower:
        filters["mounting_type"] = "snap-in"
    if "chassis" in query_lower:
        filters["mounting_type"] = "chassis"
    return filters

# Search by product name
def search_by_product_name(query):
    product_names = [normalize(p["product_name"]) for p in products]
    query_normalized = normalize(query)
    match, score, index = process.extractOne(query_normalized, product_names, scorer=fuzz.token_sort_ratio)
    if score > FUZZY_MATCH_THRESHOLD:
        return format_product_info(products[index], query)
    return None

# Search across multiple fields with advanced filters
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
            str(product.get("mounting_type", "")),
        ]))
        match_score = sum(word in combined for word in query_words)

        # Apply filters
        passes_filters = all(
            filters[key] in str(product.get(key, "")).lower()
            for key in filters
        )
        if match_score and passes_filters:
            results.append((match_score, product))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results[:MAX_RESULTS]]

# Hybrid search handler
def handle_query(query):
    result = search_by_product_name(query)
    if result:
        return result

    matches = search_by_fields(query)
    if not matches:
        return "Hmm... I couldn’t find anything that matches your query. Could you try rephrasing it?"

    return "\n\n".join(format_product_info(p, query) for p in matches)

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
