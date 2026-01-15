"""
Email Service - SMTP Email Sending

Provides functionality to send emails using SMTP configuration from system settings.
Uses Jinja2 templates for email content.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.modules.admin import service as admin_service

# Template environment setup
TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


class EmailService:
    """Email service for sending emails via SMTP"""

    def __init__(self, db: Session):
        self.db = db
        self.settings = None

    async def _load_settings(self):
        """Load SMTP settings from database"""
        if not self.settings:
            self.settings = await admin_service.get_or_create_settings(self.db)
        return self.settings

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Render both HTML and plain text templates.

        Args:
            template_name: Base name of the template (without extension)
            context: Dictionary with template variables

        Returns:
            tuple: (plain_text, html) rendered content
        """
        # Add default context variables
        default_context = {
            'workmate_url': 'https://workmate.intern.phudevelopement.xyz',
        }
        context = {**default_context, **context}

        # Render templates
        html_template = jinja_env.get_template(f"{template_name}.html")
        txt_template = jinja_env.get_template(f"{template_name}.txt")

        html = html_template.render(**context)
        text = txt_template.render(**context)

        return text, html

    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using SMTP settings from system settings.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            cc_emails: Optional list of CC recipients
            bcc_emails: Optional list of BCC recipients

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            settings = await self._load_settings()

            # Check if email is enabled
            if not settings.email_enabled:
                print("[EmailService] Email sending is disabled in system settings")
                return False

            # Validate SMTP configuration
            if not settings.smtp_host or not settings.smtp_from_email:
                print("[EmailService] SMTP configuration is incomplete")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Attach plain text body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Prepare recipient list (to + cc + bcc)
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Send email
            if settings.smtp_use_ssl:
                # Use SMTP_SSL for port 465
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg, to_addrs=all_recipients)
            else:
                # Use SMTP with STARTTLS for port 587
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    if settings.smtp_use_tls:
                        server.starttls()
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg, to_addrs=all_recipients)

            print(f"[EmailService] Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            print(f"[EmailService] Failed to send email: {str(e)}")
            return False


async def send_leave_request_notification(
    db: Session,
    request_id: str,
    employee_name: str,
    employee_email: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    total_days: str,
    approver_emails: List[str],
    reason: Optional[str] = None
) -> bool:
    """
    Send notification email when a leave request is created.

    Args:
        db: Database session
        request_id: Leave request UUID
        employee_name: Name of the employee requesting leave
        employee_email: Email of the employee
        leave_type: Type of leave (vacation, sick, etc.)
        start_date: Start date of leave
        end_date: End date of leave
        total_days: Total number of days
        approver_emails: List of approver email addresses
        reason: Optional reason for leave request

    Returns:
        bool: True if email was sent successfully
    """
    email_service = EmailService(db)

    leave_type_labels = {
        "vacation": "Urlaub",
        "sick": "Krankheit",
        "unpaid": "Unbezahlter Urlaub",
        "parental": "Elternzeit",
        "bereavement": "Trauerfall",
        "training": "Fortbildung",
        "remote": "Homeoffice",
        "other": "Sonstiges"
    }

    leave_label = leave_type_labels.get(leave_type, leave_type)

    # Render templates
    text, html = email_service._render_template('leave_request_notification', {
        'request_id': request_id,
        'employee_name': employee_name,
        'employee_email': employee_email,
        'leave_type_label': leave_label,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'reason': reason
    })

    subject = f"Neuer Urlaubsantrag von {employee_name}"

    return await email_service.send_email(
        to_emails=approver_emails,
        subject=subject,
        body=text,
        html_body=html
    )


async def send_leave_request_approved(
    db: Session,
    request_id: str,
    employee_name: str,
    employee_email: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    total_days: str,
    approver_name: str
) -> bool:
    """Send notification when leave request is approved"""
    email_service = EmailService(db)

    leave_type_labels = {
        "vacation": "Urlaub",
        "sick": "Krankheit",
        "unpaid": "Unbezahlter Urlaub",
        "parental": "Elternzeit",
        "bereavement": "Trauerfall",
        "training": "Fortbildung",
        "remote": "Homeoffice",
        "other": "Sonstiges"
    }

    leave_label = leave_type_labels.get(leave_type, leave_type)

    # Render templates
    text, html = email_service._render_template('leave_request_approved', {
        'request_id': request_id,
        'employee_name': employee_name,
        'leave_type_label': leave_label,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'approver_name': approver_name
    })

    subject = f"Urlaubsantrag genehmigt"

    return await email_service.send_email(
        to_emails=[employee_email],
        subject=subject,
        body=text,
        html_body=html
    )


async def send_leave_request_rejected(
    db: Session,
    request_id: str,
    employee_name: str,
    employee_email: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    rejection_reason: str,
    approver_name: str
) -> bool:
    """Send notification when leave request is rejected"""
    email_service = EmailService(db)

    leave_type_labels = {
        "vacation": "Urlaub",
        "sick": "Krankheit",
        "unpaid": "Unbezahlter Urlaub",
        "parental": "Elternzeit",
        "bereavement": "Trauerfall",
        "training": "Fortbildung",
        "remote": "Homeoffice",
        "other": "Sonstiges"
    }

    leave_label = leave_type_labels.get(leave_type, leave_type)

    # Render templates
    text, html = email_service._render_template('leave_request_rejected', {
        'request_id': request_id,
        'employee_name': employee_name,
        'leave_type_label': leave_label,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': 'N/A',  # Not needed for rejection
        'rejection_reason': rejection_reason,
        'approver_name': approver_name
    })

    subject = f"Urlaubsantrag abgelehnt"

    return await email_service.send_email(
        to_emails=[employee_email],
        subject=subject,
        body=text,
        html_body=html
    )


async def send_password_reset_notification(
    db: Session,
    employee_name: str,
    employee_email: str,
    admin_name: str,
    reset_date: str
) -> bool:
    """
    Send notification email when an employee's password is reset by an admin.

    Args:
        db: Database session
        employee_name: Name of the employee whose password was reset
        employee_email: Email of the employee
        admin_name: Name of the administrator who reset the password
        reset_date: Date/time when password was reset

    Returns:
        bool: True if email was sent successfully
    """
    email_service = EmailService(db)

    # Render templates
    text, html = email_service._render_template('password_reset_notification', {
        'employee_name': employee_name,
        'admin_name': admin_name,
        'reset_date': reset_date
    })

    subject = "Ihr Passwort wurde zurückgesetzt"

    return await email_service.send_email(
        to_emails=[employee_email],
        subject=subject,
        body=text,
        html_body=html
    )
