import requests
from openai import OpenAI
from write_code import write_code
from test_UI import test_UI
from check_errors import fetch_nextjs_error
import os, time
from figma_apis import parse_figma_url, fetch_figma_data, fetch_figma_image
from clean_json import process_json

global figma_url

route = "playground"
base_dir = "../samplereactproject/app/"+route
figma_url = "https://www.figma.com/design/Xss1mamz6vOArgFKyiJrPj/Untitled?node-id=0-1&p=f&t=4GOZaEpkuVgjWvbi-0"
device = "mobile"
client = OpenAI()

# Constants
MAX_ITERATIONS = 20
PROMPT = "Use Tailwinds CSS and React"
URL = "http://localhost:3000/"+route
SCREENSHOT_PATH = "screenshot_card.png"

global chat_history

# Main workflow
if __name__ == "__main__":
    try:
        requests.get(URL).status_code == 200
    except requests.ConnectionError:
        #logging.error("Development server is not running. Exiting.")
        exit(1)

    chat_history = []

    file_key, node_id = parse_figma_url(figma_url)
    figma_data = fetch_figma_data(file_key, node_id)
    if os.path.exists('reference/reference.png'):
        os.rename('reference/reference.png', 'reference/reference.png'+str(time.time())+'.png')
        with open('reference/reference.png', 'wb') as img_file:
            img_file.write(fetch_figma_image(file_key, node_id))

    if fetch_nextjs_error(URL):
        exit(1)
    else:
        if os.path.exists(base_dir+"/page.js"):
            with open('feedback.txt', 'r') as f:
                feedback = f.read()
                if feedback.strip()=="":
                    feedback = test_UI(URL, SCREENSHOT_PATH, device=device)
                    with open('feedback.txt', 'w') as f:
                        f.write(feedback)
        else:
            feedback = ""
    

    for iteration in range(MAX_ITERATIONS):

        code = write_code(PROMPT, "./reference/reference.png", process_json(figma_data), feedback, "", URL, [])
        feedback = test_UI(URL, SCREENSHOT_PATH, device=device)
        with open('feedback.txt', 'w') as f:
            f.write(feedback)
        print("waiting for feedback changes")
        with open('feedback.txt', 'r') as f:
            feedback = f.read()
        chat_history.append({"role": "assistant", "content": [{"type": "text", "text": str(code)}]})
        chat_history.append({"role": "user", "content": [{"type": "text", "text": feedback}]})
        if feedback=="":
            break