#!/usr/bin/python3
import smtplib
smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
smtpObj.starttls()
smtpObj.login('iu@iu.org.ru','Nxd14F3dk4Cchi3v4ARZ')

list = []
list.append(['Danila1','danila@posevin.com'])
list.append(['Danila2','posevin@mail.ru'])
list.append(['Danila3','posevin@bmstu.ru'])


for i in range(0,len(list)):
	smtpObj.sendmail("iu@iu.org.ru",str(list[i][1]),"Hello "+str(list[i][0])+" from robotland!")
