import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def init_lambda_driver():
    options = webdriver.ChromeOptions()

    options.binary_location = os.environ.get(
        'CHROME_PATH',
        '/opt/chrome-headless-shell-linux64/chrome-headless-shell'
    )

    # FIX FULL cho Lambda
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--no-zygote")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-features=VizDisplayCompositor")

    # temp storage
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--data-path=/tmp/data-path")
    options.add_argument("--disk-cache-dir=/tmp/cache-dir")

    # user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    service = Service(
        executable_path=os.environ.get(
            'CHROMEDRIVER_PATH',
            '/opt/chromedriver-linux64/chromedriver'
        )
    )

    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def lambda_handler(event, context):
    driver = None
    try:
        print("Start scraping...")

        driver = init_lambda_driver()
        driver.get("https://itviec.com")

        time.sleep(5)

        title = driver.title
        print(f"✅ Title: {title}")

        return {
            "statusCode": 200,
            "body": title
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": str(e)
        }

    finally:
        if driver:
            driver.quit()