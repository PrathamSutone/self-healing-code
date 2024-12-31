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
from folder_structure import generate_folder_structure

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
        
        # Extract and clean the code content
        content = match.group(2)

        # Add the standardized path and content to the FilesDict
        files_dict[path.strip()] = content.strip()

    for file_path, file_content in files_dict.items():
        folder_path = os.path.dirname(file_path)

        # Create folder structure if necessary
        if not os.path.exists(base_dir+"/"+folder_path):
            os.makedirs(base_dir+"/"+folder_path)
        
        # Write the file content
        with open(base_dir+"/"+file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        print(f"Created file: {base_dir}/{file_path}")


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
You will be given feedback on the output of the code you have written and the ideal design. You will output the MODIFIED content of the files which need to be updated to FIX the issues given, including ALL code.
Represent files like so:

FILENAME    
```
CODE
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
Do not comment on what every file does. Please note that the code should be fully functional. No placeholders.
"""

    
def create_prompt(prompt, feedback, error):
    code = ""
    if error or feedback:
        #Open code files from path
        path = "../samplereactproject/app/playground"
        files = os.listdir(path)
        for file in files:
            if os.path.isdir(f"{path}/{file}"):
                continue
            with open(f"{path}/{file}", "r") as f:
                code += f"{file}\n```\n"
                code += f.read()
    """Create a prompt based on the feedback and errors."""
    if error:
        folder_structure = generate_folder_structure("../samplereactproject/app/playground")
        return f"{folder_structure}\n------------\n{code}\n------------\n{error}\n------------\n{fix_errors}"
    if feedback:
        return f"{code}\n------------\n{feedback}\n------------\n{incorporate_feedback}"
    return f"{initial_code}\n\n{prompt}"

def generate_code(prompt, image_path, feedback, error):
    final_prompt = create_prompt(prompt, feedback, error)
    if not (error):
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

chat_output = """

**page.js**
```javascript
import AddCard from './AddCard';
import CardDetails from './CardDetails';
import ActionButtons from './ActionButtons';

export default function Page() {
  return (
    <div className="bg-black min-h-screen flex flex-col items-center space-y-6 py-6">
      <AddCard />
      <CardDetails />
      <ActionButtons />
    </div>
  );
}
```

**addcard.js**
```javascript
export default function AddCard() {
  return (
    <div className="flex justify-between items-center bg-gray-900 text-white px-6 py-4 rounded-full">
      <span>Add Your New Card 👉</span>
      <button className="bg-gray-800 rounded-full p-2">
        <span className="text-xl">+</span>
      </button>
    </div>
  );
}
```

**carddetails.js**
```javascript
export default function CardDetails() {
  return (
    <div className="bg-yellow-300 text-black rounded-xl p-6 shadow-lg text-left">
      <div className="font-bold text-xl mb-2">VISA</div>
      <div className="flex justify-between items-center mb-4">
        <span>**** **** **** 3241</span>
        <button>
          <span role="img" aria-label="icon">👁️</span>
        </button>
      </div>
      <div className="text-lg mb-1">Total Balance</div>
      <div className="text-3xl font-bold">$214,453.00</div>
    </div>
  );
}
```

**actionbuttons.js**
```javascript
export default function ActionButtons() {
  const buttons = [
    { name: 'Transfer', icon: '🤝' },
    { name: 'Request', icon: '📬' },
    { name: 'Savings', icon: '💰' },
    { name: 'Contact', icon: '📞' },
  ];

  return (
    <div className="flex justify-around w-full max-w-md">
      {buttons.map((button) => (
        <div key={button.name} className="flex flex-col items-center">
          <button className="bg-gray-800 rounded-full p-4 mb-2">
            <span role="img" aria-label={button.name}>{button.icon}</span>
          </button>
          <span className="text-white">{button.name}</span>
        </div>
      ))}
    </div>
  );
}
```

Ensure you have Tailwind CSS installed and configured in your Next.js project to use these components effectively.
"""

parse_chatgpt_output(chat_output)