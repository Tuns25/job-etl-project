import time
import json
import random
import os
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
    fresh_data = new_data
    if not fresh_data:
        print("Không có job mới.")
    all_data = old_data + new_data

    # remove duplicate theo Url
    unique = {item["Url"]: item for item in all_data if item.get("Url")}

    updated = list(unique.values())
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"Đã cập nhật {file_path}: tổng {len(updated)} job.")
def init_uc_driver(headless=False, retries=3):
    for attempt in range(1, retries + 1):
        try:
            options = uc.ChromeOptions()

            for opt in CHROME_OPTIONS_LIST:
                options.add_argument(opt)

            options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

            # 🔥 ANTI-BOT
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # 🔥 PROFILE (LOGIN)
            options.add_argument(r"--user-data-dir=D:\BCTN\chrome_profile")

            # 🔥 UI
            options.add_argument("--start-maximized")

            # ❗ chỉ dùng khi cần
            if headless:
                options.add_argument("--headless=new")

            driver = uc.Chrome(options=options, version_main=146)

            wait = WebDriverWait(driver, 20)

            print("Chrome driver khởi tạo")
            return driver, wait

        except Exception as e:
            print(f"Lỗi init driver: {e}")
            time.sleep(3)

    raise RuntimeError("Không thể khởi tạo driver")
def ensure_driver_alive(driver):
    try:
        driver.current_url
        return driver
    except:
        driver, _ = init_uc_driver(headless=False)
        return driver
def get_job_links(driver, wait, start_url):
    driver = ensure_driver_alive(driver)
    driver.get(start_url)

    print("👉 Đợi trang load...")

    time.sleep(5)

    # scroll nhiều lần (simulate user)
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(random.uniform(2, 4))

    # 🔥 CHỜ DOM THẬT (rất quan trọng)
    try:
        wait.until(lambda d: len(d.find_elements(By.TAG_NAME, "a")) > 50)
    except:
        print("⚠️ Trang load không đủ element")

    # lấy tất cả link
    links = driver.find_elements(By.TAG_NAME, "a")

    job_list = []
    seen = set()

    for link in links:
        try:
            href = link.get_attribute("href")

            # 🔥 filter job thật
            if href and ("vietnamworks.com" in href) and ("job" in href or "-jv" in href):

                if href not in seen:
                    seen.add(href)
                    job_list.append((href, None))

        except:
            continue

    print(f"👉 Lấy được {len(job_list)} job link")
    return job_list
def get_job_info(driver, job_url, retries=2):
    for attempt in range(retries):
        try:
            driver.get(job_url)
            time.sleep(random.uniform(3, 5))

            # ✅ selector đơn giản (ổn định)
            try:
                job_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                job_name = None

            try:
                company = driver.find_element(By.TAG_NAME, "h2").text.strip()
            except:
                company = None

            try:
                body = driver.find_element(By.TAG_NAME, "body").text
            except:
                body = ""

            # 🔥 tách skills đơn giản
            skills = []
            if body:
                for word in ["Python", "Java", "SQL", "AWS", "Docker"]:
                    if word.lower() in body.lower():
                        skills.append(word)

            return {
                "Job_name": job_name,
                "Company": company,
                "Posted_time": None,
                "Skills": skills,
                "Salary": None
            }

        except Exception as e:
            print(f"Retry {attempt+1} lỗi:", e)
            time.sleep(2)

    return {}
def get_company_info(driver, company_url):
    try:
        driver.get(company_url)
        time.sleep(3)

        company_name = company_size = company_industry = None

        try:
            company_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()

            if "employee" in body:
                company_size = "Unknown"

            if "it" in body:
                company_industry = "IT"

        except:
            pass

        return {
            "Company": company_name,
            "Company size": company_size,
            "Company industry": company_industry
        }

    except:
        # 🔥 luôn trả dict (KHÔNG return None)
        return {
            "Company": None,
            "Company size": None,
            "Company industry": None
        }
def main():
    driver, wait = init_uc_driver(headless=False)
    driver.get("https://www.vietnamworks.com")
    input("👉 Login xong nhấn Enter...")
    results = []
    old_urls = set()

    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            old_urls = {item.get("Url") for item in old_data if isinstance(item, dict)}
    for page in range(1,5):
        page_url = f"https://www.vietnamworks.com/jobs?q=it&page={page}&sorting=relevant"
        print(f"ĐANG CÀO TRANG {page}")
        job_list = get_job_links(driver, wait, page_url)
        for job_url, location in job_list:
            job_info = get_job_info(driver, job_url)
            if not job_info.get("Company_url"):
                continue
            company_info = get_company_info(driver, job_info["Company_url"])
            if not company_info:
                continue
            results.append({
                "Url": job_url,
                "Job name": job_info["Job_name"],
                "Company Name": company_info["Company"],
                "Address": location,
                "Company type": "At office",
                "Time": job_info["Posted_time"],
                "Skills": job_info["Skills"],
                "Job domain": job_info["Job_domain"],
                "Salary": job_info["Salary"],
                "Company industry": company_info["Company industry"],
                "Company size": company_info["Company size"],
                "Working days": "Monday-Friday"
            })
    save_or_update_json(results, JSON_PATH)
    driver.quit()
def auto_git_push(commit_msg="update data"):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Auto push thành công")
    except:
        print("Không có thay đổi hoặc push lỗi")
if __name__ == "__main__":
    main()
    auto_git_push("update: scrape data with Address & Posted/Skills fix")
