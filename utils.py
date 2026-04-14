from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def init_lambda_driver():
    options = webdriver.ChromeOptions()
    # Đường dẫn đã cài trong Dockerfile ở trên
    options.binary_location = '/opt/chrome-headless-shell-linux64/chrome-headless-shell'
    
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    
    # Quan trọng: Lambda chỉ cho phép ghi vào thư mục /tmp
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--data-path=/tmp/data-path")
    options.add_argument("--disk-cache-dir=/tmp/disk-cache")

    service = Service(executable_path='/opt/chromedriver-linux64/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver