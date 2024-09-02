import smtplib
import imghdr
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()


def send_email(image_path):
    email_message = EmailMessage()
    email_message["Subject"] = "INTRUDER ALERT!"
    email_message.set_content("Sneaky fella lurking..")

    # create python file object
    with open(image_path, "rb") as file:
        # RB - Read in binary?
        content = file.read()

    email_message.add_attachment(content, maintype="image",
                                 subtype=imghdr.what(None, content))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(os.getenv('SENDER'), os.getenv('PASSWORD'))
    gmail.sendmail(os.getenv('SENDER'), os.getenv('RECEIVER'), email_message.as_string())
    gmail.quit()

if __name__ == "__main__":
    send_email(image_path="images/50.png")

