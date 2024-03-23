import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from flask import Flask, request, jsonify, current_app

def send_email(user_email, otp):
    gmail_user = 'noreplyforekast@gmail.com'
    gmail_password = 'rxbnpjwwrzixzjq'
    message = MIMEMultipart()
    message['From'] = gmail_user
    message['To'] = user_email
    message['Subject'] = 'foreKast user email verification'
    body = MIMEText(f'Your OTP for email verification for foreKast application: {otp}')
    message.attach(body)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, user_email, message.as_string())
    # return jsonify({'message': 'Email verification otp sent'}), 200
# send_email('krishna.k15896@gmail.com', '123456')