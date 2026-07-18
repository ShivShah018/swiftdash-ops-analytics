import time
import os
from playwright.sync_api import sync_playwright

def get_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page()
    return p, page

def test_dataset(page, file_path, dataset_name):
    print(f"\n--- Testing Dataset: {dataset_name} ---")
    
    if page.locator("button:has-text('Reset / Close Dataset')").is_visible():
        page.locator("button:has-text('Reset / Close Dataset')").click()
        time.sleep(2)
        
    try:
        uploader = page.locator("input[type='file']")
        uploader.set_input_files(file_path)
    except Exception as e:
        print(f"File uploader not found: {e}")
        return False
        
    time.sleep(3)
    
    if page.locator("text=Traceback").is_visible():
        print(f"ERROR: Traceback found after uploading {dataset_name}")
        page.screenshot(path=f"qa_report/{dataset_name}_error.png")
        return False
        
    pages_to_test = ["Dynamic Dashboard", "Data Overview", "Data Quality"]
    for p_name in pages_to_test:
        print(f"Navigating to {p_name}...")
        label = page.locator(f"p:has-text('{p_name}')").first
        if label.is_visible():
            label.click()
            time.sleep(2)
            page.screenshot(path=f"qa_report/{dataset_name}_{p_name.replace(' ', '_')}.png")
            
            if page.locator("text=Traceback").is_visible():
                print(f"ERROR: Traceback found on page {p_name} for {dataset_name}")
                return False
        else:
            print(f"Page {p_name} not found in navigation.")
            
    print(f"{dataset_name} PASSED.")
    return True

if __name__ == "__main__":
    p, page = get_browser()
    try:
        os.makedirs("qa_report", exist_ok=True)
        page.goto("http://localhost:8501")
        time.sleep(3)
        titanic = os.path.abspath("data/samples/titanic.csv")
        iris = os.path.abspath("data/samples/iris.csv")
        
        test_dataset(page, titanic, "Titanic")
        test_dataset(page, iris, "Iris")
    finally:
        p.stop()
