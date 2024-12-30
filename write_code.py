import requests
import base64
from utils import encode_image 
from openai import OpenAI
client = OpenAI()
import os
teststring = 'page.js\n```jsx\nimport React from \'react\';\nimport \'./styles.css\';\n\nexport default function Page() {\n  return (\n    <div className="bg-gray-100 h-screen flex justify-center items-center">\n      <div className="bg-white shadow-md rounded-lg p-8 max-w-md w-full">\n        <div className="bg-coffee-pattern h-24 w-full rounded-t-lg"></div>\n        <h1 className="text-3xl font-bold text-center mt-6">Welcome back!</h1>\n        <p className="text-center text-gray-600 mb-8">Login to your account.</p>\n        <form>\n          <div className="mb-4">\n            <label className="block text-gray-700">Username</label>\n            <input\n              type="text"\n              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-coffee focus:ring-coffee"\n            />\n          </div>\n          <div className="mb-4">\n            <label className="block text-gray-700">Phone Number</label>\n            <input\n              type="text"\n              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-coffee focus:ring-coffee"\n            />\n          </div>\n          <button className="w-full py-2 mt-6 bg-gradient-to-r from-orange-400 to-orange-700 text-white rounded-md hover:from-orange-500 hover:to-orange-800 focus:outline-none focus:ring-2 focus:ring-coffee focus:ring-opacity-50">\n            Login\n          </button>\n        </form>\n      </div>\n    </div>\n  );\n}\n```\n\nstyles.css\n```css\n.bg-coffee-pattern {\n  background-image: url(\'coffee-pattern.png\');\n  background-size: cover;\n  border-bottom-left-radius: 0.5rem;\n  border-bottom-right-radius: 0.5rem;\n}\n\n.focus\\:border-coffee {\n  border-color: #d39b68;\n}\n\n.focus\\:ring-coffee {\n  box-shadow: 0 0 0 0.2rem rgba(211, 155, 104, 0.25);\n}\n```\n\nYou would need to include the `coffee-pattern.png` image in your public folder or adjust the path in the `styles.css` accordingly.'
base_dir = "../samplereactproject/app/playground"
import re
from files_dict import FilesDict
from check_errors import fetch_nextjs_error 

def parse_chatgpt_output(chat: str) -> FilesDict:
    """
    Converts a chat string containing file paths and code blocks into a FilesDict object.
    Ensures all files are created in the playground folder.
    
    Args:
    - chat (str): The chat string containing file paths and code blocks.

    Returns:
    - FilesDict: A dictionary with standardized file paths as keys and code blocks as values.
    """
    

    # Regex to match file paths and associated code blocks
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files_dict = FilesDict()
    for match in matches:
        # Clean and standardize the file path
        raw_path = match.group(1)
        path = re.sub(r'[\:<>"|?*]', "", raw_path)  # Remove invalid characters
        path = re.sub(r"^\[(.*)\]$", r"\1", path)  # Remove surrounding brackets
        path = re.sub(r"^`(.*)`$", r"\1", path)    # Remove surrounding backticks
        path = os.path.basename(path)             # Keep only the file name
        standardized_path = os.path.join(base_dir, path)

        # Extract and clean the code content
        content = match.group(2)

        # Add the standardized path and content to the FilesDict
        files_dict[standardized_path.strip()] = content.strip()

    for file_path, file_content in files_dict.items():
        folder_path = os.path.dirname(file_path)

        # Create folder structure if necessary
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Write the file content
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        print(f"Created file: {file_path}")




initial_code = """
You are writing react.js + next.js components with tailwinds CSS. 
You will output the file contents for any components you deem necessary to achiev the user goal.

Represent the component files like so:

FILENAME
```
CODE
```

The following tokens must be replaced like so:
FILENAME is the lowercase combined path and file name including the file extension
CODE is the code in the file

Example representation of a file:

page.js
```
export default function Page() {
    return <div>page is the parent component</div>;
    }
```

Do not comment on what every file does. Please note that the code should be fully functional. No placeholders.

Make sure to name the parent component's filename as `page.js`
"""

incorporate_feedback = """
You will be given feedback on the output of the code you have written.
You will output the MODIFIED content of the files which need to be updated to FIX the issues given, including ALL code.
Represent files like so:

FILENAME    
```
CODE
```

Example representation of a file:
page.js
```
export default function Page() {
    return <div>page is the parent component</div>;
}
```
Please note that the code should be fully functional. No placeholders. 
"""

fix_errors = """
You will output the full content of the files which need to be updated to fix the errors.
Represent files like so:

FILENAME    
```
CODE    
```

Example representation of a file:
page.js
```
export default function Page() {
    return <div>page is the parent component</div>; 
}   
```
Please note that the code should be fully functional. No placeholders.
"""

    
def create_prompt(prompt, feedback, error):
    code = ""
    if error or feedback:
        #Open code files from path
        path = "../samplereactproject/app/playground"
        files = os.listdir(path)
        for file in files:
            with open(f"{path}/{file}", "r") as f:
                code += f"{file}\n```\n"
                code += f.read()
    """Create a prompt based on the feedback and errors."""
    if error:
        return f"{code}\n------------\\n{error}\n------------\n{fix_errors}"
    if feedback:
        return f"{code}\n------------\n{feedback}\n------------\n{incorporate_feedback}"
    return f"{initial_code}\n\n{prompt}"

def generate_code(prompt, image_path, feedback, error):
    final_prompt = create_prompt(prompt, feedback, error)
    if not (feedback or error):
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "user", 
                "content":  [
                    {"type": "text", "text": final_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ]},
            ],
        )
    else:
        response = client.chat.completions.create(
            model="o1-mini", 
            messages=[
                {"role": "user", 
                "content":  [
                    {"type": "text", "text": final_prompt}
                ]},
            ],
        )
    result = response.choices[0].message.content
    print(result)
    return result


def write_code(prompt, image_path, feedback, error, URL):
    """Generate React code based on the provided prompt and image."""
    code = generate_code(prompt, image_path, feedback, error)
    parse_chatgpt_output(code)
    #run_eslint_prettier()
    error = fetch_nextjs_error(URL)  
    while error:
        #logging.info("Errors found in the UI. Generating new code.")
        code = generate_code(prompt, image_path, "", error)
        parse_chatgpt_output(code)
        error = fetch_nextjs_error(URL)



#parse_chatgpt_output(teststring)

# Example usage
chat_output = """
file:\n\n./app/playground/page.js\n```javascript\n"use client";\n\nimport { useState } from 'react';\n\nexport default function Page() {...}```
"""
#parse_chatgpt_output(chat_output)