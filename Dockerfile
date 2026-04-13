# 1. Sử dụng image Python chuẩn của AWS Lambda
FROM public.ecr.aws/lambda/python:3.11

# 2. Cài đặt các công cụ hệ thống cần thiết cho Chrome
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr 

# 3. Cài đặt Google Chrome bản ổn định
RUN curl -SL https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm > /tmp/chrome.rpm && \
    yum install -y /tmp/chrome.rpm && \
    rm /tmp/chrome.rpm

# 4. Copy requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Copy toàn bộ mã nguồn vào thư mục làm việc của Lambda
COPY . ${LAMBDA_TASK_ROOT}

# 6. Thiết lập hàm handler sẽ chạy khi Lambda kích hoạt
CMD [ "lambda_function.lambda_handler" ]