import glob
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time


def create_shot(export_dir,question_url,question_id):

    options = Options()
    options.headless = True

    driver = webdriver.Firefox(options=options, executable_path='/usr/local/bin/geckodriver')

    try:
        driver.get(question_url)

        # Wait for the page to load
        time.sleep(5)

        # Take a screenshot
        driver.save_screenshot('{0}image_{1}.png'.format(export_dir, question_id))
        print('Screenshot captured.')

    except Exception as e:
        print(f'Error navigating to Metabase question: {str(e)}')

    finally:
        driver.quit()
        # Delete all log files
        log_files = glob.glob('*.log')
        for log_file in log_files:
            os.remove(log_file)