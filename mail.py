import imghdr
import smtplib
from email.message import EmailMessage

def send_mail(html, TO_ADDRESS, content = "", name = "Arka Dutta", ):
        
    msg = EmailMessage()
    EMAIL_ADDRESS = 'arka08652@gmail.com'
    EMAIL_PASSWORD = "swec gupw jgzy fvzg"
    msg['Subject'] = f'PNR Status of {name}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg.add_header('Content-Type','text/html')

    msg.set_payload(html)
    with open(f'{name}.png', 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = f.name
    msg.add_attachment(file_data, maintype = 'image', subtype = file_type, filename = file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, TO_ADDRESS, msg.as_string())

    
