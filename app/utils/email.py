from flask import current_app
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def send_async_email(app, msg):
    """Send email in background thread so it doesn't block"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Email failed: {str(e)}')


def send_email(subject, recipients, text_body, html_body=None):
    """
    Send an email to one or more recipients
    """
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        current_app.logger.info(f'Email suppressed: {subject} to {recipients}')
        return
    
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=text_body,
        html=html_body
    )
    
    # send in background thread
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()


def send_status_update_email(user, print_request, old_status, new_status):
    """
    Notify user when their print request status changes
    """
    subject = f'Print Request {print_request.request_number} - Status Update'
    
    # build the email body
    text_body = f"""Hi {user.name},

Your print request has been updated:

Request Number: {print_request.request_number}
Document: {print_request.file_name}
Status: {old_status.replace('_', ' ').title()} → {new_status.replace('_', ' ').title()}

"""
    
    if new_status == 'completed':
        text_body += "Your print job is ready for pickup!\n\n"
    elif new_status == 'in_progress':
        text_body += "Your request is being processed.\n\n"
    elif new_status == 'cancelled':
        text_body += "Your request has been cancelled.\n\n"
    
    text_body += f"""Details:
- Pages: {print_request.number_of_pages}
- Copies: {print_request.number_of_copies}
- Format: {print_request.print_format.upper()}
- Double-sided: {'Yes' if print_request.is_double_sided else 'No'}

Thanks,
Print Request System
"""
    
    send_email(subject, [user.email], text_body)


def send_new_request_notification(admin_emails, print_request, user):
    """Let admins know about new print requests"""
    subject = f'New Print Request from {user.name}'
    
    text_body = f"""New print request submitted:

ID: #{print_request.id}
From: {user.name} ({user.email})
Department: {user.faculty_department}
Document: {print_request.document_name}
Pages: {print_request.num_pages}
Copies: {print_request.num_copies}

Please review in the admin dashboard.
"""
    
    send_email(subject, admin_emails, text_body)
