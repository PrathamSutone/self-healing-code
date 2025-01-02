import requests
from openai import OpenAI
from write_code import write_code
from test_UI import test_UI
from check_errors import fetch_nextjs_error
import os

base_dir = "../samplereactproject/app/playground"

client = OpenAI()

# Constants
MAX_ITERATIONS = 20
PROMPT = "Generate a react component for the Ratings Page. Use Tailwinds CSS and React"
URL = "http://localhost:3000/playground"
SCREENSHOT_PATH = "screenshot.png"

global chat_history

# Main workflow
if __name__ == "__main__":
    try:
        requests.get(URL).status_code == 200
    except requests.ConnectionError:
        #logging.error("Development server is not running. Exiting.")
        exit(1)

    chat_history = []

    if fetch_nextjs_error(URL):
        exit(1)
    else:
        if os.path.exists(base_dir+"/page.js"):
            with open('feedback.txt', 'r') as f:
                feedback = f.read()
                if feedback=="":
                    feedback = test_UI(URL, SCREENSHOT_PATH)
                    with open('feedback.txt', 'w') as f:
                        f.write(feedback)
        else:
            feedback = ""
    
    for iteration in range(MAX_ITERATIONS):
        code = write_code(PROMPT, "./reference/reference.png", feedback, "", URL, chat_history)
        feedback = test_UI(URL, SCREENSHOT_PATH)
        with open('feedback.txt', 'w') as f:
            f.write(feedback)
        print("waiting for feedback changes")
        with open('feedback.txt', 'r') as f:
            feedback = f.read()
        chat_history.append({"role": "assistant", "content": [{"type": "text", "text": str(code)}]})
        chat_history.append({"role": "user", "content": [{"type": "text", "text": feedback}]})
        if feedback=="":
            break