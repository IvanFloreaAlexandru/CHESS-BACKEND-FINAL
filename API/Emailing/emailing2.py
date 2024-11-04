import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import dotenv_values
from starlette.templating import Jinja2Templates

env_vars = dotenv_values(".env")

HOST = env_vars.get("HOST")
PORT = env_vars.get("PORT")
FROM_EMAIL = env_vars.get("FROM_EMAIL")
GOOGLE_APP_PASSWORD = env_vars.get("GOOGLE_APP_PASSWORD")
TO_EMAIL = "a@yahoo.ro"


def send_email(host, port, from_email, password, to_email, subject, message):
    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    smtp.login(from_email, password)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'html'))

    smtp.send_message(msg)
    smtp.quit()


templates = Jinja2Templates(directory="templates")


async def send_email_with_attachment(host, port, from_email, password, to_email, subject, template_name,
                                     template_context, attachment=None):
    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(from_email, password)

            message = templates.TemplateResponse(template_name, template_context).body.decode('utf-8')

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'html'))

            if attachment:
                attachment_mime = MIMEApplication(attachment.getvalue(), _subtype="octet-stream")
                attachment_mime.add_header('Content-Disposition', 'attachment', filename='qrcode.png')
                msg.attach(attachment_mime)

            smtp.send_message(msg)
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
