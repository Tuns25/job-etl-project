# Sử dụng Amazon Linux 2 làm nền tảng (ổn định hơn cho việc cài Chromium)
FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hệ thống cơ bản
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr gzip tar unzip

# 2. Cài đặt Chromium từ kho EPEL (Kho mở rộng của Fedora cho doanh nghiệp)
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum install -y chromium

# 3. Copy và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy toàn bộ mã nguồn
COPY . ${LAMBDA_TASK_ROOT}

# 5. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]