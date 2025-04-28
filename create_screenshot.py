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

        # Wait until the page base HTML is fully loaded
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Wait until the loading spinner disappears
        try:
            WebDriverWait(driver, 30).until_not(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Loading')]"))
            )
        except Exception as e:
            print(f"Warning: Timeout waiting for loading spinner to disappear - {str(e)}")

        # Allow a little extra time for final rendering
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
