FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hệ thống cho Chrome và công cụ Build cho Python
# Thêm gcc, gcc-c++ và python3-devel để sửa lỗi build NumPy/Pandas
RUN yum update -y && yum install -y \
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
    libX11-xcb \
    gcc \
    gcc-c++ \
    python3-devel \
    && yum clean all

# 2. Tải bản Chrome Headless Shell và Driver (Phiên bản ổn định)
RUN curl -Lo /tmp/chrome-headless-shell.zip https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chrome-headless-shell-linux64.zip && \
    unzip /tmp/chrome-headless-shell.zip -d /opt/ && \
    curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    rm /tmp/chrome-headless-shell.zip /tmp/chromedriver.zip

# 3. Cài đặt thư viện Python
# Bước này cực kỳ quan trọng: Nâng cấp pip/setuptools trước khi cài requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy mã nguồn vào thư mục task của Lambda
COPY . ${LAMBDA_TASK_ROOT}

# 5. Cấp quyền thực thi cho Chrome và Driver (Dọn dẹp lại lệnh chmod)
RUN chmod +x /opt/chrome-headless-shell-linux64/chrome-headless-shell /opt/chromedriver-linux64/chromedriver

# 6. Biến môi trường để Selenium biết đường dẫn (Tùy chọn nhưng nên có)
ENV CHROME_PATH=/opt/chrome-headless-shell-linux64/chrome-headless-shell
ENV CHROMEDRIVER_PATH=/opt/chromedriver-linux64/chromedriver

# 7. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]