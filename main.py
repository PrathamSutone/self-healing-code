import requests
from openai import OpenAI
client = OpenAI()

# Constants
MAX_ITERATIONS = 8
PROMPT = "Generate a React component for a user-friendly home page UI based on the provided image. Use Tailwinds CSS. "
URL = "http://localhost:3000/playground"
SCREENSHOT_PATH = "screenshot.png"



# Main workflow
if __name__ == "__main__":
    try:
        requests.get(URL).status_code == 200
    except requests.ConnectionError:
        #logging.error("Development server is not running. Exiting.")
        exit(1)

    feedback = ""
    for iteration in range(MAX_ITERATIONS):
        write_code(PROMPT, "./reference/reference.png", feedback)
        feedback = test_UI(PROMPT, URL, SCREENSHOT_PATH)
        if feedback=="":
            break