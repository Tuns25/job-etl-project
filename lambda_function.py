import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def init_lambda_driver():
    # Dọn dẹp /tmp để tránh tràn bộ nhớ khi tái sử dụng container
    user_data_dir = '/tmp/user-data'
    if os.path.exists(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)

    options = webdriver.ChromeOptions()
    
    # Chỉ định đường dẫn binary đã cài trong Docker
    options.binary_location = os.environ.get('CHROME_PATH')
    
    # Các tham số bắt buộc cho Lambda
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    
    # Cấu hình lưu trữ tạm
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--data-path=/tmp/data-path")
    options.add_argument("--disk-cache-dir=/tmp/disk-cache")

    service = Service(executable_path=os.environ.get('CHROMEDRIVER_PATH'))
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def lambda_handler(event, context):
    driver = None
    try:
        driver = init_lambda_driver()
        
        # Test thử truy cập ITviec
        url = "https://itviec.com"
        driver.get(url)
        
        page_title = driver.title
        print(f"Successfully accessed: {page_title}")

        return {
            "statusCode": 200,
            "body": {
                "message": "Cào dữ liệu thành công!",
                "title": page_title
            }
        }
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {
            "statusCode": 500,
            "body": str(e)
        }
    finally:
        if driver:
            driver.quit()