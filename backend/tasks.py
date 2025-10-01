import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2

# Load environment variables
load_dotenv()

# Template setup
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "emails")
template_loader = jinja2.FileSystemLoader(template_dir)
template_env = jinja2.Environment(loader=template_loader)

# SMTP Configuration
my_email = os.getenv("MY_EMAIL")
password = os.getenv("PASSWORD")

def user_registration_email(email, username):
    """Send welcome email to newly registered user using SMTP."""
    try:
        # Load HTML template
        template = template_env.get_template("welcome_email.html")
        html_content = template.render(
            username=username,
            frontend_url=os.getenv('FRONTEND_URL', 'http://localhost:3000')
        )
        
        # Create plain text version
        text_content = f"""Hi {username},

Welcome to SplitFree! You have successfully signed up to our platform.

Start splitting expenses with your friends and family.

Best regards,
The SplitFree Team"""
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Welcome to SplitFree! 🎉"
        message["From"] = f"Splitwise <{my_email}>"
        message["To"] = email
        
        # Add text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()  # Encrypt the connection
            connection.login(user=my_email, password=password)
            connection.send_message(message)
        
        return True
        
    except Exception as e:
        raise e

def expense_notification_email(email, username, expense_description, amount, group_name, payer_name=None, expense_date=None, group_id=None, your_share=None):
    """Send notification when user is involved in a new expense using SMTP."""
    try:
        # Load HTML template
        template = template_env.get_template("expense_notification.html")
        html_content = template.render(
            username=username,
            group_name=group_name,
            expense_description=expense_description,
            expense_amount=f"{amount:.2f}",
            payer_name=payer_name or "Unknown",
            expense_date=expense_date or "Today",
            group_id=group_id,
            your_share=f"{your_share:.2f}" if your_share else None,
            frontend_url=os.getenv('FRONTEND_URL', 'http://localhost:3000')
        )
        
        # Create plain text version
        text_content = f"""Hi {username},

You have been added to a new expense in {group_name}:

Expense: {expense_description}
Amount: ${amount:.2f}
Paid by: {payer_name or 'Unknown'}

{f'Your share: ${your_share:.2f}' if your_share else ''}

Log in to SplitFree to see the details and settle up.

Best regards,
The SplitFree Team"""

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"New expense in {group_name} - ${amount:.2f}"
        message["From"] = f"SplitFree <{my_email}>"
        message["To"] = email
        
        # Add text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.send_message(message)
        
        return True
        
    except Exception as e:
        raise e

def settlement_notification_email(email, username, amount, payer_name, group_name, payee_name=None, group_id=None):
    """Send notification when user receives a settlement using SMTP."""
    try:
        # Load HTML template
        template = template_env.get_template("settlement_notification.html")
        html_content = template.render(
            username=username,
            group_name=group_name,
            settlement_amount=f"{amount:.2f}",
            payer_name=payer_name,
            payee_name=payee_name or username,
            group_id=group_id,
            frontend_url=os.getenv('FRONTEND_URL', 'http://localhost:3000')
        )
        
        # Create plain text version
        text_content = f"""Hi {username},

Great news! You received a payment in {group_name}:

Amount: ${amount:.2f}
From: {payer_name}

Your balance has been updated in SplitFree.

Best regards,
The SplitFree Team"""

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Payment received: ${amount:.2f} from {payer_name}"
        message["From"] = f"SplitFree <{my_email}>"
        message["To"] = email
        
        # Add text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.send_message(message)
        
        return True
        
    except Exception as e:
        raise e