import glob
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_shot(export_dir, question_url, question_id):
    options = Options()
    options.headless = True  # Run in headless mode

    driver = webdriver.Firefox(options=options, executable_path='/usr/local/bin/geckodriver')

    try:
        driver.get(question_url)

        # Wait until the page has completely loaded
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Optional: Wait for a specific element to appear (modify selector as needed)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            print(f"Warning: Timeout while waiting for body tag - {str(e)}")

        # Allow additional time for any dynamic content
        time.sleep(2)

        # Take a screenshot
        screenshot_path = os.path.join(export_dir, f"image_{question_id}.png")
        driver.save_screenshot(screenshot_path)
        print(f'Screenshot captured: {screenshot_path}')

    except Exception as e:
        print(f'Error navigating to Metabase question: {str(e)}')

    finally:
        driver.quit()

        # Delete all log files
        log_files = glob.glob('*.log')
        for log_file in log_files:
            os.remove(log_file)

