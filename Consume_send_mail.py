from kafka import KafkaConsumer
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
sender_email = "521h0447@student.tdtu.edu.vn"
password = "29062003Ace#"
def send_mail(receiver,subject,body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
    # Kết nối đến máy chủ SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Sử dụng SMTP của Gmail
        server.starttls()  # Bật bảo mật TLS
        server.login(sender_email, password)  # Đăng nhập

        # Gửi email
        server.send_message(msg)
        logging.info("Email sent successfully!")

    except Exception as e:
        logging.exception(f"Failed to send email: {e}")

    finally:
        server.quit()  
# Kết nối đến Kafka
consumer = KafkaConsumer(
    'send-email',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='mai'
)

# Lắng nghe các thông điệp
for message in consumer:
    order_event = message.value  
    logging.info(f"Received order event: {order_event}")
    send_mail(order_event['email'], order_event['subject'], order_event['message'])