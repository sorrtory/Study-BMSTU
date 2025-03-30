#!/usr/bin/python3
import smtplib

def getData():

	array=[]
	my_file = open("./db.txt", "r")
	my_string = my_file.read()
	my_file.close()

	lines = my_string.split("\n")
	for i in range(0,len(lines)-1):
		lines_cols = lines[i].split("::")
		print(str(i+1),end=") ")
		for j in range(0,len(lines_cols)):
			print(lines_cols[j],end="\t")
		array.append([lines_cols[2],lines_cols[3]])
		print("")
		#print(array)
	return array

smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.starttls()
smtpObj.login('robotland2@gmail.com','12345678990robotland')

list = getData()
#print(list)

for i in range(0,len(list)):

	from_addr = "robotland2@gmail.com"
	to_addr = str(list[i][1])
	subject = "Hi to "+str(list[i][0])
	body_text = "Hello "+str(list[i][0])+" from robotland!"

	BODY = "\r\n".join(("From: %s" % from_addr,"To: %s" % to_addr,"Subject: %s" % subject,"",body_text ))
	print(BODY)
	smtpObj.sendmail("robotland2@gmail.com",str(list[i][1]),BODY)
