FROM public.ecr.aws/lambda/python:3.11

# Cài đặt các thư viện cần thiết cho Chrome
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXscrnsaver \
    utils-linux-ng mesa-libgbm libgbm libwayland-client libwayland-server \
    adwaita-cursor-theme adwaita-icon-theme hicolor-icon-theme \
    libX11-xcb pango cario libXft-devel \
    vulkan-loader xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel nss nspr

# Cài đặt Chromium và Driver trực tiếp từ kho của Amazon
RUN yum install -y chromium-browser chromium-driver

# Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.lambda_handler" ]