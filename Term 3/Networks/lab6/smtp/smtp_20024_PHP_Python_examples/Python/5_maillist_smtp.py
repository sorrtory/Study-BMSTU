#!/usr/bin/python3
import smtplib
smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
smtpObj.starttls()
smtpObj.login('robotland2@yandex.ru','fcogbelywgwutrbh')

list = []
list.append(['Danila1','danila@posevin.com'])
list.append(['Danila2','posevin@mail.ru'])
list.append(['Danila3','posevin@bmstu.ru'])


for i in range(0,len(list)):

	from_addr = "robotland2@yandex.ru"
	to_addr = str(list[i][1])
	subject = "Hi to "+str(list[i][0])
	body_text = "Hello "+str(list[i][0])+" from robotland!"


	BODY = "\r\n".join(("From: %s" % from_addr,"To: %s" % to_addr,"Subject: %s" % subject,"",body_text ))
	print(BODY)
	smtpObj.sendmail("robotland2@yandex.ru",str(list[i][1]),BODY)
