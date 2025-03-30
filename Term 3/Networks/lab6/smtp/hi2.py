# Looking to send emails in production? Check out our Email API/SMTP product!
import smtplib

sender = "Private Person <from@example.com>"
receiver = "trysmpt@yandex.com"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
    server.starttls()
    server.login("29e7e443ac5c67", "103f19c77960e3")
    server.sendmail(sender, receiver, message)