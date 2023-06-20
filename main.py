import socks
import smtplib, ssl, threading, time
import poplib
import random
from email.parser import Parser
from email.message import EmailMessage

config  = {}
customers = []
initial_msg = ''
reply_msg = ''
total_general_count = 0
total_reply_count = 0

def load_config(config_file):
    config_vars = {}
    with open(config_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                var, value = line.split('=', 1)
                config_vars[var.strip()] = value.strip()
    return config_vars

def read_file_line_by_line(file, strip = False):

    lines = []
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if strip:
        lines = [line.strip() for line in lines]
    return lines

def read_file(file):
    content = ""
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def load_customers(recipients_file):
    return read_file_line_by_line(recipients_file, True)

def select_random_msg(file):
  first_messages = read_file_line_by_line(file)
  lengthOfLines = len(first_messages)

  rand = random.randrange(0, lengthOfLines)
  tmp_msg = first_messages[rand]
  start_index = -1
  end_index = -1
  count = 0
  starts = []
  ends = []
  while True:
      start_index = tmp_msg.find("{", start_index + 1)
      end_index = tmp_msg.find("}", end_index + 1)
      if start_index == -1 | end_index == -1:
          break
      starts.append(start_index)
      ends.append(end_index)
      count += 1     
  final_msg = ""
  if(count == 0):
      return tmp_msg
  else:
      for x in starts:
          order = starts.index(x)
          if (order == 0):
              prevsection = tmp_msg[0 :x]
              final_msg += prevsection
          else:
              prevsection = tmp_msg[ends[order-1] + 1: x]
              final_msg += prevsection
          components = tmp_msg[x + 1: ends[order]].split("|")
          components_length = len(components)
          final_msg += components[random.randrange(0, components_length)]
      final_msg += tmp_msg[ends[len(starts)-1] + 1:]
  return final_msg

def send_email(content, subject, recipient, index, email_type):
    list_senders = read_file_line_by_line("./assets/senders.txt")
    try:
        smtp_server = config.get('smtp_server')
        smtp_port = 465
        smtp_username = list_senders[index - 1].split(",")[0]
        smtp_password = list_senders[index - 1].split(",")[1]
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            global total_general_count
            global total_reply_count
            server.login(smtp_username, smtp_password)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = subject
            msg['From'] = smtp_username
            msg['To'] = recipient
            server.send_message(msg, from_addr=smtp_username, to_addrs=recipient)
            print("----------------------------------------------->")
            print("Account " + smtp_username + " : " + "LOGIN TRUE")
            if(email_type != "reply"):
                total_general_count += 1
                print(smtp_username + " successfuly sent MESSAGE to " + recipient + "! :  " + "Total Email Sends: " + format(total_general_count))
            else:
                total_reply_count += 1
                print(smtp_username + " successfuly sent MESSAGE to " + recipient + "! :  " + "Total Reply Email Sends: " + format(total_reply_count))
            with open("./assets/verify.txt", "a", encoding="utf-8") as verify_txt:
                verify_lists = read_file_line_by_line("./assets/verify.txt")
                if(smtp_username + "\n" not in verify_lists):
                    verify_txt.write(smtp_username + "\n")
            server.quit()

    except Exception as e:
        # print('Error(send_email): ', e)
        print("----------------------------------------------->")
        print("Account " + smtp_username + " : " + "LOGIN FALSE")
        with open("./assets/disabled.txt", "a", encoding="utf-8") as disabled_txt:
            disabled_lists = read_file_line_by_line("./assets/disabled.txt")
            if(smtp_username + "\n" not in disabled_lists):
                disabled_txt.write(smtp_username + "\n")
        
def smtp_sender():
    smtp_interval = 30
    list_senders = read_file_line_by_line("./assets/senders.txt")
    list_recipients = read_file_line_by_line("customers.txt")
    num_recipients = len(list_recipients)
    num_senders = len(list_senders)

    index = 1
    while index < num_senders + 1:
        content = select_random_msg("./assets/First Message 200 Eng.txt")
        recipient = list_recipients[random.randrange(0, num_recipients)]
        subject='{0}'.format(recipient.split('@')[0])
        send_email(content, subject ,recipient, index, "")

        if index == num_senders:
            index = 1
        else:
            index += 1
        
        time.sleep(smtp_interval)
        
def get_email(str):
    try:
        start = str.index('<')
        end = str.index('>')
        return str[start + 1: end]
    except ValueError:
        return str    

def save_user_reply(user, reply):
    with open('user-reply.txt', "+wb") as fp:
        fp.write('reply from : {}\r\n'.format(user).encode('utf-8'))
        
        fp.write(reply.as_bytes())
        
        # if reply['content-type'].maintype == 'text':
        #     if reply['content-type'].subtype == 'plain':
        #         fp.writelines(reply.get_content().splitlines())
        #     elif reply['content-type'].subtype == 'html':
        #         fp.write(reply.get_content())
        #     else:
        #         print("Don't know how to display {}".format(reply.get_content_type()))
        # elif reply['content-type'].content_type == 'multipart/related':
        #     body = reply.get_body(preferencelist=('html'))
        #     fp.write(body)
        # else:
        #     print("Don't know how to display {}".format(reply.get_content_type()))


def pop3_receiver(pop_user, pop_password, index):
    time.sleep(50)
    pop3_server = config.get('pop3_server')
    pop3_interval = int(config.get('pop3_interval'))
    user = pop_user
    password = pop_password
    
    link_lists = read_file_line_by_line("./assets/links test.txt")
    num_link = len(link_lists)
    
    while True:
        try:
            pop3 = poplib.POP3_SSL(pop3_server)
            pop3.user(user)
            pop3.pass_(password)
            items = pop3.list()[1]
            ids = [int(item.split()[0]) for item in items]
            for id in ids:
                text = pop3.retr(id)[1]
                text = b'\r\n'.join(text).decode('utf-8')
                
                msg = Parser().parsestr(text)
                sender = get_email(msg['From'])
                receiver = get_email(msg['To'])
                subject = msg['Subject']
                if receiver == user and sender in customers:
                    # reply with the second email
                    save_user_reply(sender, msg)
                    reply_content = select_random_msg("./assets/Reply Message 200 Eng.txt").split(":")[0] + " : " + link_lists[random.randrange(0, num_link)]
                    reply_subject = subject
                    print("----------------------------------------------->")
                    print(reply_subject)
                    send_email(reply_content, reply_subject, sender, index, "reply")
                    pop3.dele(id)
            pop3.quit()
        except Exception as e:
            print('pop3_receiver: ', e)
        time.sleep(pop3_interval)

def init():
    global config
    global customers
    global initial_msg
    global reply_msg
    
    config = load_config("config.txt")
    customers = load_customers("customers.txt")
    initial_msg = select_random_msg("./assets/First Message 200 Eng.txt")
    reply_msg = select_random_msg("./assets/Reply Message 200 Eng.txt")

def main():
    try:
        init()

        socks.setdefaultproxy(socks.SOCKS5, '91.221.37.187', 1080)
        socks.wrapmodule(smtplib)
        

        list_senders = read_file_line_by_line("./assets/senders.txt")
        index = 1
        for sender in list_senders:
            username = sender.split(",")[0]
            password = sender.split(",")[1]
            threading.Thread(target = lambda : pop3_receiver(username, password, index)).start()
            index += 1

        thread_sender = threading.Thread(target = smtp_sender)
        thread_sender.start()        
        thread_sender.join()

    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print("An error occured: ", e)

if __name__ == "__main__":
    main()
