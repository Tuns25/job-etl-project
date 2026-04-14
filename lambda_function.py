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

    # 🔥 giả lập user thật
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    options.add_argument("--window-size=1920,1080")

    service = Service(
        executable_path=os.environ.get(
            'CHROMEDRIVER_PATH',
            '/opt/chromedriver-linux64/chromedriver'
        )
    )

    driver = webdriver.Chrome(service=service, options=options)

    # 🔥 ẩn dấu selenium
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def lambda_handler(event, context):
    driver = None
    try:
        print("🚀 Start scraping...")

        driver = init_lambda_driver()

        driver.get("https://itviec.com")

        # ✅ delay phải đặt ở đây
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