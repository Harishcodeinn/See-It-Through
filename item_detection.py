import smtplib

# Email configuration
sender_email = "harishptce@gmail.com"
receiver_email = "harishptce@gmail.com"
app_password  = "umox qonp ukik krnn"



try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, app_password)
    message = "Subject: Test Email\n\nThis is a test email from Python."
    server.sendmail(sender_email, receiver_email, message)
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Error:", e)
