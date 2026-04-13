# Sử dụng base image chính thức của AWS cho Python
FROM public.ecr.aws/lambda/python:3.11

# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện (pandas, requests,...)
RUN pip install -r requirements.txt

# Copy toàn bộ code vào container
COPY . ${LAMBDA_TASK_ROOT}

# Chỉ định hàm xử lý chính (ví dụ file là lambda_function.py, hàm là lambda_handler)
CMD [ "lambda_function.lambda_handler" ]
