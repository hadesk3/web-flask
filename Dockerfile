# Sử dụng image Python làm cơ sở
FROM python:3.9
RUN apt-get update && apt-get install -y netcat-openbsd

WORKDIR /app
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn ứng dụng vào container
COPY . .


# Mở cổng cho ứng dụng Flask
EXPOSE 5000

# Chạy ứng dụng Flask

