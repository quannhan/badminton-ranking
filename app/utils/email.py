# =====================================================
# FILE: app/utils/email.py
# =====================================================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email: str, subject: str, body: str):
    """Gửi email thông báo"""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_inactive_warning(user_email: str, user_name: str, days_inactive: int):
    """Gửi email cảnh báo không hoạt động"""
    subject = "⚠️ Cảnh báo: Bạn đã không chơi lâu rồi!"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Xin chào {user_name}!</h2>
            <p>Bạn đã không tham gia trận đấu nào trong <strong>{days_inactive} ngày</strong>!</p>
            <p>🏸 Hãy quay lại sân và "lên kèo" để giữ vững thứ hạng của bạn!</p>
            <p>Câu lạc bộ đang chờ đợi bạn!</p>
            <br>
            <p>Trân trọng,<br>Ban quản lý CLB Cầu lông</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body)