FROM public.ecr.aws/lambda/python:3.11

# 1. Cài đặt các thư viện hệ thống cần thiết
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr gzip tar

# 2. Tải và cài đặt Chromium + Driver (Phiên bản chuyên dụng cho Lambda)
# Chúng ta dùng bản của adieuadieu để đảm bảo chạy được trong môi trường hạn chế của Lambda
RUN curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017.03.tar.gz | tar -xz -C /opt/ && \
    curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    rm /tmp/chromedriver.zip

# 3. Copy và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy toàn bộ mã nguồn
COPY . ${LAMBDA_TASK_ROOT}

# 5. Khởi chạy
CMD [ "lambda_function.lambda_handler" ]