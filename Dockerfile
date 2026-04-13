FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hệ thống cần thiết
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr gzip tar unzip

# 2. Tải Chromium và Driver phiên bản ổn định (v119 - Khớp với code của bạn)
# Sử dụng link từ nhà phát triển chrome-aws-lambda
RUN curl -SL https://github.com/Sparticuz/chromium/releases/download/v119.0.2/chromium-v119.0.2-layer.x86_64.tar.gz | tar -xz -C /opt/ && \
    curl -SL https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip > /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    rm /tmp/chromedriver.zip

# 3. Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy mã nguồn
COPY . ${LAMBDA_TASK_ROOT}

# 5. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]