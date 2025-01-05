import json
def clean_json(data):
    # Remove dictionaries with a single key-value pair and replace with the value
    if isinstance(data, dict):
       
        if len(data.values()) == 1:
            return clean_json(next(iter(data.values())))
        else:
            return {key: clean_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
    else:
        return data

def rgba_to_hex(color):
    """Convert RGBA color dictionary to HEX format."""
    r = int(color['r'] * 255)
    g = int(color['g'] * 255)
    b = int(color['b'] * 255)
    a = int(color['a'] * 255)
    if color['a'] == 1 or color['a'] == 0:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

def replace_color_with_hex(data):
    """Recursively replace color objects with their HEX representation."""
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if (key == "color" or key=="backgroundColor") and isinstance(value, dict):
                try:
                    # Replace the 'color' object with the hex code
                    new_data[key] = rgba_to_hex(value)
                except KeyError:
                    # Skip if the 'color' object is incomplete
                    print(f"Incomplete color object found: {value}")
                    continue
            else:
                new_data[key] = replace_color_with_hex(value)
        return new_data

    elif isinstance(data, list):
        # Process each item in the list
        return [replace_color_with_hex(item) for item in data]

    else:
        # Return scalar values as is
        return data
    
def remove_key_value_pairs(data, config):
    keys_to_remove = config.get("keys_to_remove", [])
    key_value_pairs_to_remove = config.get("key_value_pairs_to_remove", [])

    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            # Check if the key is in the keys_to_remove list
            if key in keys_to_remove:
                #print(f"Removing key: {key}")
                continue
            
            if any({key: value} == pair for pair in key_value_pairs_to_remove):
                #print(f"Removing key-value pair: {key}: {value}")
                continue
            
            # Recursively clean nested structures
            cleaned_data[key] = remove_key_value_pairs(value, config)
        return cleaned_data

    elif isinstance(data, list):
        # Process each item in the list
        return [remove_key_value_pairs(item, config) for item in data]

    else:
        # Return scalar values as is
        return data

# Load the configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file) 

with open("figma.json", "r") as file:
    figma_data = json.load(file)

print(len(str(figma_data)))
cleaned_data = replace_color_with_hex(figma_data)


# Clean the JSON data
cleaned_data = remove_key_value_pairs(cleaned_data, config)
print("Cleaned JSON Data")
print(len(str(cleaned_data)))

#cleaned_data = clean_json(cleaned_data)

# Output the cleaned JSON
with open("cleaned_output.json", "w") as output_file:
    json.dump(cleaned_data, output_file, indent=0)