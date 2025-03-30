# Looking to send emails in production? Check out our Email API/SMTP product!
import smtplib

# sender = "Private Person <from@example.com>"
# receiver = "A Test User <to@example.com>"

# sender = " trysmpt@yandex.com"
# receiver = "posevin@proton.me>"


# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}

# This is a test e-mail message."""

# with smtplib.SMTP("smtp.yandex.ru", 587) as server:
#     server.starttls()
#     server.login("trysmpt@yandex.com", "mcjcmsxckrifuxsb")
#     server.sendmail(sender, receiver, message)



#!/usr/bin/python3
import smtplib
smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
smtpObj.starttls()
smtpObj.login('trysmpt@yandex.com','mcjcmsxckrifuxsb')
smtpObj.sendmail("trysmpt@yandex.com","orlando20056@yandex.ru","Hello from robotland!")