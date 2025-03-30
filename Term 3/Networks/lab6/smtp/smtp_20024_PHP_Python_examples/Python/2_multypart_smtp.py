#!/usr/bin/python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("sending email")

smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
smtpObj.starttls()
smtpObj.login('iu9@bmstu.posevin.ru','XquuuStE1XXGsSB2EtVw')
#subject = "Test email from Python"
to_addr = "danila@posevin.com"
from_addr = "iu9@bmstu.posevin.ru"
#body_text = "<b>Python rules them all!</b>"

msg = MIMEMultipart('alternative')

msg['Subject'] = "My subj"
msg['From'] = from_addr
msg['To'] = to_addr
text = "Hi there!"
html = "<b>test</b><table border=\"1\"><tr><td>11</td><td>12</td></tr></table>"
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')
part3 = MIMEText(html+"1234567890", 'html')

msg.attach(part1)
msg.attach(part2)
msg.attach(part1)

smtpObj.sendmail("iu9@bmstu.posevin.ru","danila@posevin.com",msg.as_string())
