import time
import json
import random
import os
import subprocess
from dotenv import load_dotenv
import undetected_chromedriver as uc
from datetime import datetime
from utils import init_uc_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import boto3
from botocore.exceptions import NoCredentialsError

# Cấu hình AWS - Nên dùng Environment Variables để bảo mật
# Tải thông tin từ file .env
load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = 'job-market-bronze-layer'

def upload_to_s3(file_name, s3_path):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_KEY)
    try:
        s3.upload_file(file_name, BUCKET_NAME, s3_path)
        print(f" Tải lên S3 thành công: {s3_path}")
    except Exception as e:
        print(f"Lỗi tải lên S3: {e}")
START_URL = "https://www.vietnamworks.com/it-kw"
BASE_URL = "https://www.vietnamworks.com"
JSON_PATH = "vietnamworks_it_filtered.json"
CHROME_OPTIONS_LIST = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-gpu",
    "--incognito",
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.179 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
]
def save_or_update_json(new_data, file_path=JSON_PATH):
    if os.path.exists(file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                old_data = json.load(f)
                if not isinstance(old_data, list):
                    old_data = []
        except:
            old_data = []
    else:
        old_data = []
    old_urls = {item.get("Url") for item in old_data if isinstance(item, dict) and item.get("Url")}
    fresh_data = [job for job in new_data if job.get("Url") not in old_urls]
    if not fresh_data:
        print("Không có job mới.")
        return
    updated = fresh_data + old_data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"Đã cập nhật {file_path}: tổng {len(updated)} job.")
def ensure_driver_alive(driver):
    try:
        driver.current_url
        return driver
    except:
        driver, _ = init_uc_driver(headless=False)
        return driver
def get_job_links(driver, wait, start_url, limit=9999):
    driver = ensure_driver_alive(driver)
    driver.get(start_url)
    time.sleep(7)
    
    # 1. Tiêu diệt popup và mở khóa cuộn trang
    try:
        driver.execute_script("""
            var overlays = document.querySelectorAll('[role="dialog"], div[data-testid="modal"]');
            overlays.forEach(e => e.remove());
            document.body.style.overflow = 'auto';
        """)
        print("Đã xử lý popup chặn màn hình.")
        time.sleep(1)
    except Exception as e:
        pass

    seen_urls = set()
    job_list = []
    stagnant_rounds = 0

    while True:
        # Cuộn trang xuống
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(random.uniform(1.5, 3.5))

        # 2. Thu gom TẤT CẢ các đường link nằm trong khu vực tìm kiếm
        try:
            job_links = driver.find_elements(By.CSS_SELECTOR, "div.search-result a")
        except:
            job_links = []
        
        current_count = len(seen_urls)

        for link_elem in job_links:
            try:
                job_url = link_elem.get_attribute("href")
                if not job_url:
                    continue
                    
                url_lower = job_url.lower()
                
                # 3. MÀNG LỌC: Bỏ qua các link dẫn đến trang công ty hoặc link rác
                if "company" in url_lower or "cong-ty" in url_lower or "nha-tuyen-dung" in url_lower:
                    continue
                if len(job_url) < 30 or "javascript" in url_lower:
                    continue

                if job_url not in seen_urls:
                    seen_urls.add(job_url)
                    if not job_url.startswith("http"):
                        job_url = BASE_URL + job_url
                    
                    # Trích xuất địa điểm (dùng Try-Except để tránh lỗi nếu cấu trúc thẻ thay đổi)
                    try:
                        parent_text = link_elem.find_element(By.XPATH, "../..").text
                        location = parent_text.strip().split('\n')[-1] 
                        # Nếu lấy nhầm chuỗi quá dài (không phải tên tỉnh), gán mặc định là Vietnam
                        if len(location) > 30: 
                            location = "Vietnam"
                    except:
                        location = "Vietnam"

                    job_list.append((job_url, location))
            except:
                continue

        # Kiểm tra xem có load thêm được link mới không
        if len(seen_urls) == current_count:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
            
        if stagnant_rounds >= 5:
            break

    print(f"Đã tìm thấy {len(job_list)} công việc trên trang này.")
    return job_list[:limit]
def get_job_info(driver, job_url):
    driver.get(job_url)
    time.sleep(random.uniform(2, 4))
    job_name = salary = posted_time = skills = job_domain = None
    company_url = None
    try:
        job_name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except: pass
    try:
        salary = driver.find_element(By.CSS_SELECTOR, "span.sc-ab270149-0.cVbwLK").text.strip()
    except: pass
    try:
        company_a = driver.find_element(By.CSS_SELECTOR, "div.sc-37577279-3.drWnZq a.sc-ab270149-0.egZKeY")
        company_url = company_a.get_attribute("href")
    except: pass
    try:
        info_blocks = driver.find_elements(By.CSS_SELECTOR, "div.sc-7bf5461f-1.jseBPO div")
        for block in info_blocks:
            try:
                label = block.find_element(By.CSS_SELECTOR, "label").text.strip().upper()
                value = block.find_element(By.CSS_SELECTOR, "p, span").text.strip()
                if not value:
                    continue
                if "POSTED DATE" in label:
                    posted_time = value
                elif "SKILL" in label:
                    skills = value
                elif "JOB FUNCTION" in label:
                    job_domain = value
            except:
                continue
    except:
        pass
    return {
        "Job_name": job_name,
        "Salary": salary,
        "Posted_time": posted_time,
        "Skills": skills,
        "Job_domain": job_domain,
        "Company_url": company_url
    }
def get_company_info(driver, company_url):
    driver.get(company_url)
    time.sleep(3)
    company_name = company_size = company_industry = None
    try:
        company_name = driver.find_element(By.CSS_SELECTOR, "div.sc-ca95509a-6.cXJgQF h1.sc-ca95509a-8.gcvyPj").text.strip()
    except: pass
    lis = driver.find_elements(By.CSS_SELECTOR, "ul.sc-7f4c261d-5.kfIkVN li.sc-7f4c261d-6.ejuuLs")
    for li in lis:
        try:
            label = li.find_element(By.CSS_SELECTOR, "p.type").text.strip().lower()
            value = li.find_element(By.CSS_SELECTOR, "p.text").text.strip()
            if "size" in label: company_size = value
            if "industry" in label: company_industry = value
        except:
            continue
    if not company_size:
        return None
    return {
        "Company": company_name,
        "Company size": company_size,
        "Company industry": company_industry
    }
# --- HÀM TỰ ĐỘNG PUSH (Cải tiến để không lỗi trên Cloud) ---
def auto_git_push_code_only(commit_msg):
    # Nếu chạy trên Cloud, hàm này sẽ tự thoát ngay lập tức
    if os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        return 
    try:
        subprocess.run(["git", "add", "vietnamworks_scraper.py"], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🚀 Đã cập nhật mã nguồn lên GitHub.")
    except Exception:
        print("⚠️ Bỏ qua Git Push (Có thể do môi trường hoặc không có thay đổi).")

# --- HÀM CHÍNH (THAY THẾ MAIN) ---
def run_scraper():
    # Tự động nhận diện: Nếu trên Cloud thì chạy ẩn (True), nếu máy nhà thì hiện Chrome (False)
    is_cloud = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
    driver, wait = init_uc_driver(headless=is_cloud) 
    
    results = []
    old_urls = set()

    # Bước 1: Kiểm tra dữ liệu cũ
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                old_urls = {item.get("Url") for item in old_data if isinstance(item, dict)}
        except: pass

    try:
        # Bước 2: Cào dữ liệu
        for page in range(1, 40):
            page_url = f"https://www.vietnamworks.com/jobs?q=it&page={page}&sorting=relevant"
            job_list = get_job_links(driver, wait, page_url)
            
            for job_url, location in job_list:
                if job_url in old_urls: continue
                job_info = get_job_info(driver, job_url)
                if not job_info.get("Company_url"): continue
                
                # SỬA LỖI QUAN TRỌNG: Phải truyền 'driver' vào hàm này
                company_info = get_company_info(driver, job_info["Company_url"])
                if not company_info: continue
                
                results.append({
                    "Url": job_url,
                    "Job name": job_info["Job_name"],
                    "Company Name": company_info["Company"],
                    "Address": location,
                    "Salary": job_info["Salary"],
                    "Company industry": company_info["Company industry"],
                    "Company size": company_info["Company size"]
                })

        # Bước 3 & 4: Lưu local và đẩy lên S3 Bronze
        if results:
            save_or_update_json(results, JSON_PATH)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"vietnamworks/raw/vnw_data_{timestamp}.json"
            upload_to_s3(JSON_PATH, s3_key)

    finally:
        # Luôn đóng trình duyệt để tránh tràn RAM
        driver.quit()
        # Chạy Git Push nếu đang ở Local
        auto_git_push_code_only(f"Update scraper: {datetime.now()}")

if __name__ == "__main__":
    run_scraper()