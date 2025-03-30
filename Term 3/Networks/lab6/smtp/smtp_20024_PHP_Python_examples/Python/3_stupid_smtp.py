#!/usr/bin/python3
import smtplib
smtpObj = smtplib.SMTP('mail.nic.ru', 587)
smtpObj.starttls()
smtpObj.login('3@dactyl.su','12345678990qwertyuiOOp')

for i in range(0,3):
	smtpObj.sendmail("3@dactyl.su","danila@posevin.com","Hello "+str(i)+" from robotland!")
