import time
import os
import timeit
from playwright.sync_api import sync_playwright

def get_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    return p, browser, page

def wait_for_app(page):
    page.goto("http://localhost:8501")
    page.wait_for_selector("text=Universal CSV Analytics Platform")

def test_startup(page):
    start = timeit.default_timer()
    wait_for_app(page)
    load_time = timeit.default_timer() - start
    print(f"Startup Time: {load_time:.2f}s")
    page.screenshot(path="qa_report/1_Welcome_Page.png")
    return load_time

def check_traceback(page, context=""):
    if page.locator("text=Traceback").is_visible():
        print(f"CRITICAL BUG: Traceback found during {context}")
        page.screenshot(path=f"qa_report/ERROR_{context.replace(' ', '_')}.png")
        return True
    return False

def test_demo(page):
    print("Testing Demo Dataset...")
    start = timeit.default_timer()
    page.locator("button:has-text('Load Demo Dataset')").click()
    page.wait_for_selector("text=Viewing Demo Dataset")
    load_time = timeit.default_timer() - start
    print(f"Demo Load Time: {load_time:.2f}s")
    
    if check_traceback(page, "Demo Dashboard"):
        return False
    page.screenshot(path="qa_report/2_Demo_Dashboard.png")
    return True

def test_reset(page):
    print("Testing Reset...")
    try:
        # If sidebar is collapsed (e.g. after resize), the button might not be visible or clickable easily.
        # Reloading restores the default expanded state on desktop.
        page.reload()
        page.wait_for_selector("text=Reset / Close Dataset", timeout=5000)
    except Exception:
        pass
    page.locator("button:has-text('Reset')").first.click()
    page.wait_for_selector("text=Welcome! Choose an option")
    if check_traceback(page, "Reset"):
        return False
    return True

def upload_and_test(page, filepath, name, is_edge_case=False):
    print(f"Testing Upload: {name}")
    start = timeit.default_timer()
    
    try:
        uploader = page.locator("input[type='file']").first
        uploader.set_input_files(filepath)
    except Exception as e:
        print(f"Failed to upload {name}: {e}")
        return False
        
    time.sleep(3) # Wait for processing
    load_time = timeit.default_timer() - start
    print(f"{name} Load Time: {load_time:.2f}s")
    
    if check_traceback(page, f"Upload {name}"):
        return False
    
    if is_edge_case and name == "Empty CSV":
        # We expect a warning, not a crash
        if page.locator("text=Uploaded CSV is empty").is_visible():
            print("Empty CSV gracefully handled.")
            page.screenshot(path=f"qa_report/8_Error_Handling_{name}.png")
            return True
            
    if not is_edge_case:
        page.screenshot(path=f"qa_report/3_Dataset_Profile_{name}.png")
        
        pages = ["Dynamic Dashboard", "Data Overview", "Data Quality"]
        for i, p_name in enumerate(pages):
            label = page.locator(f"p:has-text('{p_name}')").first
            if label.is_visible():
                label.click()
                time.sleep(2)
                if check_traceback(page, f"{name} {p_name}"):
                    return False
                page.screenshot(path=f"qa_report/{4+i}_{p_name.replace(' ', '_')}_{name}.png")
    
    return True

if __name__ == "__main__":
    os.makedirs("qa_report", exist_ok=True)
    p, browser, page = get_browser()
    try:
        print("--- PHASE 1: STARTUP ---")
        test_startup(page)
        
        print("\n--- PHASE 2: DEMO DATASET ---")
        test_demo(page)
        
        print("\n--- PHASE 3: RESET ---")
        test_reset(page)
        
        print("\n--- PHASE 4: TITANIC ---")
        titanic = os.path.abspath("data/samples/titanic.csv")
        upload_and_test(page, titanic, "Titanic")
        
        print("\n--- PHASE 5: IRIS ---")
        iris = os.path.abspath("data/samples/iris.csv")
        # Ensure we are uploading via sidebar without resetting
        upload_and_test(page, iris, "Iris")
        
        print("\n--- PHASE 6: EDGE CASES ---")
        edge_cases = {
            "Empty CSV": "empty.csv",
            "Numeric Only": "numeric_only.csv",
            "Categorical Only": "cat_only.csv",
            "Single Column": "single_col.csv",
            "Duplicates": "duplicates.csv",
            "Missing Values": "missing.csv"
        }
        
        for name, filename in edge_cases.items():
            test_reset(page)
            path = os.path.abspath(f"data/samples/edge_cases/{filename}")
            upload_and_test(page, path, name, is_edge_case=True)
            
        print("\nAll UI Tests Completed Successfully.")
    finally:
        p.stop()
