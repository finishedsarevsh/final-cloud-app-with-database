import os
import time
from playwright.sync_api import sync_playwright

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
screenshots_dir = r'C:\Users\91770\.gemini\antigravity\scratch\final-cloud-app-with-database\screenshots'
os.makedirs(screenshots_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=edge_path, headless=True)

    # ---------------------------------------------------------
    # Step 1: Admin site screenshot (03-admin-site.png)
    # ---------------------------------------------------------
    admin_context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = admin_context.new_page()
    page.goto('http://127.0.0.1:8000/admin/')

    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'admin12345')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')

    # Confirm sections
    content = page.content()
    assert "Authentication and Authorization" in content, "Authentication section missing"
    assert "Onlinecourse" in content or "ONLINECOURSE" in content, "Onlinecourse section missing"
    print("Admin site verified successfully.")

    admin_screenshot_path = os.path.join(screenshots_dir, '03-admin-site.png')
    page.screenshot(path=admin_screenshot_path, full_page=True)
    print(f"Saved admin screenshot to {admin_screenshot_path}")
    admin_context.close()

    # ---------------------------------------------------------
    # Step 2: Student flow & final result screenshot (07-final.png)
    # ---------------------------------------------------------
    user_context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = user_context.new_page()
    page.goto('http://127.0.0.1:8000/onlinecourse/login/')

    page.fill('input[name="username"]', 'student1')
    page.fill('input[name="psw"]', 'student12345')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

    # Open course 1 details
    page.goto('http://127.0.0.1:8000/onlinecourse/1/')
    page.wait_for_load_state('networkidle')

    # Click 'Start Exam' button to reveal the collapsible questions form
    start_exam_btn = page.query_selector('button[data-target="#exam"]')
    if start_exam_btn:
        start_exam_btn.click()
        page.wait_for_timeout(1000)

    # Select correct choices:
    # Q1: models.py
    # Q2: python manage.py migrate
    # Q3: POST and GET
    choices_to_select = ["models.py", "python manage.py migrate", "POST", "GET"]
    labels = page.query_selector_all('label.form-check-label')
    for label in labels:
        text = label.inner_text().strip()
        for target in choices_to_select:
            if target == text or target in text:
                checkbox = label.query_selector('input[type="checkbox"]')
                if checkbox and not checkbox.is_checked():
                    checkbox.check()
                    print(f"Checked answer: {text}")

    # Submit form
    page.click('input[type="submit"][value="Submit"]')
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(1000)

    result_content = page.content()
    assert "Congratulations" in result_content, "Congratulations message missing on result page"
    assert "100/100" in result_content, "Score 100/100 missing on result page"
    print("Final exam results verified successfully with 100/100 score and Congratulations message!")

    final_screenshot_path = os.path.join(screenshots_dir, '07-final.png')
    page.screenshot(path=final_screenshot_path, full_page=True)
    print(f"Saved final screenshot to {final_screenshot_path}")
    user_context.close()

    browser.close()
    print("Verification complete!")
