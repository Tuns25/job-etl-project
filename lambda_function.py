import undetected_chromedriver as uc

def init_lambda_driver():
    options = uc.ChromeOptions()

    options.binary_location = os.environ.get(
        'CHROME_PATH',
        '/opt/chrome-headless-shell-linux64/chrome-headless-shell'
    )

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(
        driver_executable_path=os.environ.get(
            'CHROMEDRIVER_PATH',
            '/opt/chromedriver-linux64/chromedriver'
        ),
        options=options,
        use_subprocess=False
    )

    return driver