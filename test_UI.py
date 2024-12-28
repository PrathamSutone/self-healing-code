
from playwright.sync_api import sync_playwright

def take_screenshot(url, output_path):
    """Take a screenshot of the specified URL."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("main")  # Ensure main content is loaded
        page.screenshot(path=output_path)
        browser.close()
    #logging.info(f"Screenshot saved to {output_path}")

def get_ui_feedback(screenshot_path):
    """Use GPT-4 Vision to analyze the UI and provide feedback."""
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "user", 
             "content":  [
                {"type": "text", "text": "Analyze the UI and provide feedback."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot_path)}"}},
            ]},
        ],
        )
        return response.choices[0].message.content
    except Exception as e:
        #logging.error(f"Error getting UI feedback: {e}")
        raise

def feedback_is_positive(feedback):