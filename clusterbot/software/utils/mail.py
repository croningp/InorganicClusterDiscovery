import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText

SERVER = "smtp-mail.outlook.com"
PORT = 587

USERNAME = "croningp_platforms@outlook.com"
PASSWD = "tcgweig2002"

def send_email(platform_name, toaddr, body, flag=0):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = toaddr

    if flag == 0:
        msg['Subject'] = "{} Update".format(platform_name)
    elif flag == 1:
        msg["Subject"] = "CRASH -- {} Error".format(platform_name)
    elif flag == 2:
        msg["Subject"] = "{} -- Vial Tray Full".format(platform_name)

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SERVER, PORT)
    server.starttls()
    server.login(USERNAME, PASSWD)
    text = msg.as_string()
    server.sendmail(USERNAME, toaddr, text)
    server.quit()


def notify(platform_name, emails, msg, flag=0):
    try:
        for addr in emails:
            send_email(platform_name, addr, msg, flag=flag)
    except Exception as e:
        if "Spam" in e.__str__():
            print("Apparently we're spamming...")
        else:
            print(e)
