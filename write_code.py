import requests
import base64

def capture_screen_errors(page):
    """Check the page for React error messages displayed on the screen."""
    try:
        error_selector = "body *:has-text('Error')"  # Adjust selector to match React's error display
        error_elements = page.query_selector_all(error_selector)
        errors = [element.text_content().strip() for element in error_elements]
        return errors if errors else None
    except Exception as e:
        logging.error(f"Error capturing screen errors: {e}")
        return None

def generate_code(prompt, image_path):
    """Call ChatGPT API to generate React code based on the given prompt and image."""
    base64_image = encode_image(image_path)
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini", 
    #     messages=[
    #         {"role": "user", 
    #          "content":  [
    #             {"type": "text", "text": prompt},
    #             {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
    #         ]},
    #     ],
    # )
    str = """
    import React from 'react';

    const Card = ({ title, description, image, link }) => {
    return (
        <div className="max-w-sm rounded-lg overflow-hidden shadow-lg bg-white">
        {image && (
            <img className="w-full h-48 object-cover" src={image} alt={title} />
        )}
        <div className="p-4">
            <h2 className="text-2xl font-semibold text-gray-800">{title}</h2>
            <p className="mt-2 text-gray-600">{description}</p>
            {link && (
            <a
                href={link}
                className="mt-4 inline-block text-blue-500 hover:underline"
            >
                Learn More
            </a>
            )}
        </div>
        </div>
    );
    };

    export default Card;
    """
    return str

def write_code_to_file(code):
    """Write the generated code to the appropriate file until all erorr are resolved."""
    while(capture_screen_errors(URL)):
        logging.info("Errors found in the UI. Generating new code.")
        code = generate_code(PROMPT, "./reference/reference.png")
    file_path = "../samplereactproject/app/playground/page.js"
    with open(file_path, "w") as file:
        file.write(code)
    logging.info(f"Code written to {file_path}")

def run_eslint_prettier():
    """Run ESLint and Prettier to validate and format code."""
    try:
        subprocess.run(["npx", "eslint", "--fix", "../samplereactproject/app/playground/page.js"], check=True)
        logging.info("Code linted and formatted successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"ESLint/Prettier error: {e}")
        raise
    
def write_code(prompt, image_path, feedback, error, URL):
    """Generate React code based on the provided prompt and image."""
    code = generate_code(prompt, image_path)
    write_code_to_file(code)
    #run_eslint_prettier()
    
    while error:
        #logging.info("Errors found in the UI. Generating new code.")
        code = generate_code(prompt, image_path, "", error)
        write_code_to_file(code)
        error = capture_screen_errors(URL)