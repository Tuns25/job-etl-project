FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hệ thống cần thiết cho Chrome (Amazon Linux 2023)
RUN yum install -y \
    unzip \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    alsa-lib \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXscrnsaver \
    mesa-libgbm \
    libgbm \
    pango \
    cairo \
    nss \
    nspr \
    vulkan-loader \
    xdg-utils \
    libX11-xcb

# 2. Cài đặt Chrome & Driver (Sử dụng bản build ổn định cho Lambda)
# Thay vì các bản cũ, chúng ta cài bản Chrome Headless Shell hiện đại
# 2. Tải bản Chrome Headless Shell và Driver (Phiên bản mới, link trực tiếp từ Google)
RUN curl -Lo /tmp/chrome-headless-shell.zip https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chrome-headless-shell-linux64.zip && \
    unzip /tmp/chrome-headless-shell.zip -d /opt/ && \
    curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    rm /tmp/chrome-headless-shell.zip /tmp/chromedriver.zip

# Cấp quyền thực thi
RUN chmod +x /opt/chrome-headless-shell-linux64/chrome-headless-shell /opt/chromedriver-linux64/chromedriver

# 3. Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy mã nguồn (bao gồm utils.py, itviec_scraper.py...)
COPY . ${LAMBDA_TASK_ROOT}

# 5. Cấp quyền thực thi cho Chrome/Driver
RUN chmod +x /opt/chrome-headless-shell-linux64/chrome-headless-shell /opt/chromedriver-linux64/chromedriver

# 6. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]