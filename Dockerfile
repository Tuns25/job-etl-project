# Sử dụng Image được tối ưu sẵn cho Lambda + Selenium + Chrome
# Đây là Image cực kỳ nổi tiếng của umihico, giúp bạn bỏ qua bước cài Chrome thủ công
FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hỗ trợ cần thiết
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr unzip

# 2. Tải bản Chrome và Driver được build riêng cho Lambda (không lỗi yum)
RUN curl -Lo /tmp/chrome-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome/119.0.6045.105/linux64/chrome-linux64.zip && \
    unzip /tmp/chrome-linux64.zip -d /opt/ && \
    curl -Lo /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome/119.0.6045.105/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip

# 3. Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy mã nguồn
COPY . ${LAMBDA_TASK_ROOT}

# 5. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]