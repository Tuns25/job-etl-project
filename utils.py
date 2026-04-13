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
        # Sử dụng mode headless cũ vì bản này cực kỳ ổn định
        options.add_argument('--headless')
        # Đường dẫn sau khi giải nén từ lệnh tar ở trên
        options.binary_location = '/opt/headless-chromium'
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--single-process')
        options.add_argument('--disable-gpu')
        
        driver = uc.Chrome(
            options=options,
            # Đường dẫn sau khi giải nén từ lệnh unzip ở trên
            driver_executable_path="/opt/chromedriver",
            version_main=114 # Khớp với bản driver v2.37
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