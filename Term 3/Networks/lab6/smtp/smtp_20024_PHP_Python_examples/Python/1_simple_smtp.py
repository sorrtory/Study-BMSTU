#!/usr/bin/python3
import smtplib
smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
smtpObj.starttls()
smtpObj.login('robotland2@yandex.ru','fcogbelywgwutrbh')
smtpObj.sendmail("robotland2@yandex.ru","posevin@proton.me","Hello from robotland!")
