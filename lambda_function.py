import itviec_scraper
import itjobs_scraper
import vietnamworks_scraper

def lambda_handler(event, context):
    print("--- Khởi động quy trình ETL ---")

    # Gọi hàm run_scraper từ các file bạn đã sửa ở bước 2
    itviec_scraper.run_scraper()
    itjobs_scraper.run_scraper()
    vietnamworks_scraper.run_scraper()

    return {
        'statusCode': 200,
        'body': 'Tất cả scraper đã chạy xong!'
    }
