from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import shutil

def init_lambda_driver():
    # 1. Dọn dẹp thư mục /tmp trước khi chạy (Tùy chọn)
    # Lambda có thể tái sử dụng container, đôi khi /tmp bị đầy
    user_data_dir = '/tmp/user-data'
    if os.path.exists(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)

    options = webdriver.ChromeOptions()
    
    # Đường dẫn đã cài trong Dockerfile
    options.binary_location = '/opt/chrome-headless-shell-linux64/chrome-headless-shell'
    
    # Các tham số bắt buộc cho môi trường không giao diện (Headless)
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process') # Cực kỳ quan trọng trong Lambda
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    
    # 2. Quản lý bộ nhớ đệm và dữ liệu người dùng trong /tmp
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--data-path=/tmp/data-path")
    options.add_argument("--disk-cache-dir=/tmp/disk-cache")
    
    # 3. Giảm bớt log không cần thiết để tránh tràn log CloudWatch
    options.add_argument("--log-level=3")
    options.add_argument("--silent")

    service = Service(
        executable_path='/opt/chromedriver-linux64/chromedriver',
        log_output=os.devnull # Không ghi log driver ra stdout
    )
    
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver