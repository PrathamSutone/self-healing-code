import re
import requests

# Constants
FIGMA_API_BASE_URL = "https://api.figma.com/v1"
FIGMA_TOKEN = "figd_17LrvYpi7VvrJHBk-mzMuwrnmeWckNkI7JfJbneU"  # Replace with your Figma PAT

# Function to parse Figma URL
def parse_figma_url(figma_url):
    pattern = r"https:\/\/www\.figma\.com\/design\/(?P<file_key>[a-zA-Z0-9]+)(?:\/[^?]*)?(?:\?.*?node-id=(?P<node_id>[a-zA-Z0-9:\-]+))?"
    match = re.search(pattern, figma_url)
    if not match:
        raise ValueError("Invalid Figma URL")
    
    file_key = match.group("file_key")
    node_id = match.group("node_id")
    return file_key, node_id

# Function to make API calls
def fetch_figma_data(file_key, node_id=None):
    headers = {
        "X-FIGMA-TOKEN": FIGMA_TOKEN
    }
    
    if node_id:
        endpoint = f"{FIGMA_API_BASE_URL}/files/{file_key}/nodes"
        params = {"ids": node_id}
    else:
        endpoint = f"{FIGMA_API_BASE_URL}/files/{file_key}"
        params = {}
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
    return response.json()



# Main execution
if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/Xss1mamz6vOArgFKyiJrPj/Untitled?node-id=0-6&t=QkjWn8yYY3zBR4rn-0"
    
    try:
        file_key, node_id = parse_figma_url(figma_url)
        print(f"File Key: {file_key}, Node ID: {node_id}")
        
        # Fetch data from Figma API
        figma_data = fetch_figma_data(file_key, node_id)
        print("Figma Data Retrieved")
        print(figma_data)
    except Exception as e:
        print(f"Error: {e}")

