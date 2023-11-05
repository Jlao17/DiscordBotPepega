# Your example API responses as dictionaries
json1 = {
    "results": [{}, {}, {}],
    "item_count": 30
}

json2 = {
    "results": [{}, {}, {}],
    "item_count": 30
}

# Merge the "results" from both responses
merged_results = json1["results"] + json2["results"]

# Create a new dictionary with the merged results and the item_count
merged_response = {
    "results": merged_results,
    "item_count": json1["item_count"] + json2["item_count"]
}

# Print the merged response
print(merged_response)