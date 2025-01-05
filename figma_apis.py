import re
import requests
import os
import json

# Constants
FIGMA_API_BASE_URL = "https://api.figma.com/v1"
figma_token = os.getenv("FIGMA_TOKEN")

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
        "X-FIGMA-TOKEN": figma_token
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

def fetch_figma_image(file_key, node_id, format="png", scale=2):
    """
    Fetches an image of a specific node from Figma.
    
    Args:
    - file_key (str): The Figma file key.
    - node_id (str): The node ID of the object to export.
    
    Returns:
    - bytes: The image data in bytes.
    
    Raises:
    - Exception: If the API request fails or returns an error.
    """
    headers = {
        "X-FIGMA-TOKEN": figma_token
    }
    
    # Figma Image Export API endpoint
    endpoint = f"{FIGMA_API_BASE_URL}/images/{file_key}?ids={node_id}"
    
    # Send the request to the Figma API
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
    # Get the image URL from the response
    image_data = response.json()

    image_url = image_data['images'][node_id.replace("-", ":")]


    print(f"Image URL: {image_url}")
    
    # Download the image from the URL
    img_response = requests.get(image_url)

    
    if img_response.status_code != 200:
        raise Exception(f"Error downloading image: {img_response.status_code}")
    
    # Return the image data in bytes
    return img_response.content


# Main execution
if __name__ == "__main__":
    figma_url = "https://www.figma.com/design/Xss1mamz6vOArgFKyiJrPj/Untitled?node-id=0-1&p=f&t=2elaW5tzalQWvgxk-0"
    
    try:
        file_key, node_id = parse_figma_url(figma_url)
        print(f"File Key: {file_key}, Node ID: {node_id}")  
        
        # Fetch data from Figma API
        figma_data = fetch_figma_data(file_key, node_id)
        print("Figma Data Retrieved")

        with open('figma_data.json', 'w') as f:
            f.write(json.dumps(figma_data, indent=4))
        
        image_data = fetch_figma_image(file_key, node_id)
        
        # Save the image locally
        with open("reference/reference.png", "wb") as img_file:
            img_file.write(image_data)

    except Exception as e:
        print(f"Error: {e}")

