import socks
import smtplib
import ssl
from email.message import EmailMessage

def send_email(content, subject, recipient):
    try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465
        smtp_username = 'omargtr24@gmail.com'
        smtp_password = 'djurwjqtpbuoafny'
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_username, smtp_password)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = "Subject"
            msg['To'] = recipient
            server.send_message(msg, from_addr=smtp_username, to_addrs=recipient)
            server.quit()
    except Exception as e:
        print('Error(send_email): ', e)


send_email('Content', 'Subject', 'oliverlim818@gmail.com')