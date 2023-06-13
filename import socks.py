import socks
import imaplib
import ssl
from email.message import EmailMessage
import time

def send_email(content, subject, recipient):
    try:
        imap_server = 'imap.gmail.com'
        imap_port = 993
        imap_username = 'uchitosato@gmail.com'
        imap_password = 'eeekahpyfwhuazqg'
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(imap_server, imap_port) as server:
            server.login(imap_username, imap_password)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = "Subject"
            msg['To'] = recipient
            server.append('Inbox', "", imaplib.Time2Internaldate(time.time()), str(msg).encode('utf-8'))
            server.logout()
    except Exception as e:
        print('Error(send_email): ', e)

socks.setdefaultproxy(socks.SOCKS5, "91.221.37.187", 1080)
socks.wrapmodule(imaplib)

try:
    send_email('Are you there now?', 'Subject', 'afoucher7255@gmail.com')
    print("success-------------->")
except:
    print("failed!!!!!!!!!!!!!!!!")