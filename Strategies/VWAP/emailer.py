
import smtplib
import email

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import datetime


##now = datetime.datetime.now()
##timeToExit = now + datetime.timedelta(hours=1)


MY_ADDRESS = "bkd2703@uncw.edu"
PASSWORD = "LilaBear#1"


def sendEmail(instrument,entryPrice):

    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(MY_ADDRESS, PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = MY_ADDRESS
    msg['To'] = MY_ADDRESS
    msg['Subject'] = "Trade Entered"

    body = instrument + "\t" + "Entry: " + str(entryPrice)
    msg.attach(MIMEText(body, 'plain'))

    server.login(MY_ADDRESS, PASSWORD)
    text = msg.as_string()
    server.sendmail(MY_ADDRESS, MY_ADDRESS, text)
    server.quit()

