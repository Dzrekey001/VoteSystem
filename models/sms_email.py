         
import smtplib, requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

class Send():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_email_passwd = os.getenv("ADMIN_PASSWORD")

    def __init__(self, token, first_name) -> None:
        self.first_name=first_name
        self.token = token
        self.message_content = f"""Hi {self.first_name}\nThank you for being a part of this exciting MVP stage of the voting system!\nTake a moment to test by clicking on the unique link below:\nhttp://127.0.0.1:5000/login?token={token}"""
    
    #send email messages
    def send_email(self, voter_email_address):
        message = MIMEMultipart()
        message["From"] = f"Vote <{self.admin_email}>"
        message["To"] = voter_email_address
        message["Subject"] = f"Testing Voting Sytem"
        message.attach(MIMEText(self.message_content, "plain"))
        text = message.as_string()
        try:
            with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
                connection.starttls()
                connection.login(user=self.admin_email,password=self.admin_email_passwd)
                connection.sendmail(from_addr=self.admin_email, to_addrs=voter_email_address,msg=text)
                return "email sent successfully."
        except Exception as e:
            print (e)
    
    def send_sms(self, contact):
        SENDER_ID = "DKD"
        #send sms
        try:
            sms_content = self.message_content
            response = requests.get(f"https://sms.arkesel.com/sms/api?action=send-sms&api_key=Y2xlQWJFYWpXTUhzSVFLcWtGZEo& to={contact}&from={SENDER_ID}&sms={self.message_content}")
            response.raise_for_status()
            return "sms successfully sent."
        except Exception as e:
            print(e)