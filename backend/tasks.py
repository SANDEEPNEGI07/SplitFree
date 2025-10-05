import os
import jinja2
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gmail_email = os.getenv("GMAIL_EMAIL")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
template_loader = jinja2.FileSystemLoader(template_dir)
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename, **context):
    try:
        return template_env.get_template(template_filename).render(**context)
    except Exception as e:
        logger.error(f"Template rendering failed for {template_filename}: {str(e)}")
        raise

def send_email_with_gmail(to_email, subject, html_content, plain_text):
    """
    Send email using Gmail SMTP
    """
    if not gmail_email or not gmail_password:
        logger.error("Missing Gmail credentials (GMAIL_EMAIL or GMAIL_APP_PASSWORD)")
        return {"status": "error", "message": "Missing Gmail credentials"}
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"SplitFree <{gmail_email}>"
        message["To"] = to_email
        
        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(html_content, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(gmail_email, gmail_password)
            server.sendmail(gmail_email, to_email, message.as_string())
            
        logger.info(f"Gmail email sent successfully to {to_email}")
        return {"status": "success", "message": "Email sent successfully via Gmail"}
        
    except Exception as e:
        logger.error(f"Failed to send Gmail email to {to_email}: {str(e)}")
        return {"status": "error", "message": f"Gmail SMTP error: {str(e)}"}

def send_user_registration_email(email, username):
    try:
        html_content = render_template("emails/welcome_email.html", username=username)
        plain_text = f"{username}, You have successfully signed up to SplitFree! Welcome to our expense sharing platform."
        
        logger.info(f"Attempting to send welcome email via Gmail SMTP to {email}")
        result = send_email_with_gmail(
            email,
            "Successfully signed up!",
            html_content,
            plain_text
        )
        
        if result["status"] == "success":
            logger.info(f"Welcome email sent successfully to {email}")
        else:
            logger.error(f"Failed to send welcome email to {email}: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to send registration email to {email}: {str(e)}")
        return {"status": "error", "message": str(e)}