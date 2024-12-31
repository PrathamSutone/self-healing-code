import requests
from openai import OpenAI
from write_code import write_code
from test_UI import test_UI

base_dir = "../samplereactproject/app/playground"

client = OpenAI()

# Constants
MAX_ITERATIONS = 8
PROMPT = "Generate three React components based on the provided image. One for add your card, one for card details, one for th ebuttons below it. Use Tailwinds CSS."
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
        write_code(PROMPT, "./reference/reference.png", feedback, "", URL)
        feedback = test_UI(URL, SCREENSHOT_PATH)
        if feedback=="":
            break