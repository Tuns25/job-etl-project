import os
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait

def init_uc_driver(headless=True):
    """
    Hàm khởi tạo Driver dùng chung cho tất cả Scrapers.
    Tự động tương thích giữa máy Local (Windows) và Cloud (Linux/Docker).
    """
    options = uc.ChromeOptions()
    
    # Các tham số tối ưu RAM và CPU cho môi trường Docker/Lambda
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    
    # Giả lập User Agent để tránh bị chặn
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument(f'--user-agent={user_agent}')

    # Kiểm tra xem có đang chạy trên AWS Lambda không
    is_cloud = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

    if is_cloud:
        # Cấu hình BẮT BUỘC cho môi trường Cloud
        options.add_argument('--headless')
        # Trỏ đúng vào file đã giải nén trong Dockerfile
        options.binary_location = '/opt/headless-chromium'
        
        # Lambda chỉ cho phép ghi vào /tmp
        options.add_argument('--user-data-dir=/tmp/user-data')
        options.add_argument('--data-path=/tmp/data-path')
        options.add_argument('--homedir=/tmp')
        options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        
        driver = uc.Chrome(
            options=options,
            # SỬA DÒNG NÀY: Trỏ vào /opt/chromedriver thay vì /usr/bin/
            driver_executable_path="/opt/chromedriver",
            version_main=119
        )
    else:
        # Chạy ở máy Local (Windows)
        if headless:
            options.add_argument('--headless')
        
        driver = uc.Chrome(options=options)

    # Thiết lập kích thước màn hình chuẩn
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 20)
    
    return driver, wait