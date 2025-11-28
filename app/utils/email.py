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
    subject = f'Print Request #{print_request.id} - Status Update'
    
    # build the email body
    text_body = f"""Hi {user.name},

Your print request has been updated:

Request ID: #{print_request.id}
Document: {print_request.document_name}
Status: {old_status.replace('_', ' ').title()} → {new_status.replace('_', ' ').title()}

"""
    
    if new_status == 'approved':
        text_body += "Good news! Your request has been approved.\n\n"
    elif new_status == 'rejected':
        text_body += f"Your request was rejected.\nReason: {print_request.admin_notes or 'No reason provided'}\n\n"
    elif new_status == 'completed':
        text_body += "Your print job is ready for pickup!\n\n"
    elif new_status == 'in_progress':
        text_body += "Your request is being processed.\n\n"
    
    text_body += f"""Details:
- Pages: {print_request.num_pages}
- Copies: {print_request.num_copies}
- Color: {'Yes' if print_request.color else 'No'}
- Double-sided: {'Yes' if print_request.double_sided else 'No'}

Thanks,
Print Request System
"""
    
    # HTML version looks nicer
    status_color = {
        'approved': '#27ae60',
        'completed': '#17a2b8',
        'rejected': '#e74c3c',
        'in_progress': '#f39c12'
    }.get(new_status, '#6c757d')
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Print Request Status Update</h2>
        
        <p>Hi <strong>{user.name}</strong>,</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Request ID:</strong> #{print_request.id}</p>
            <p><strong>Document:</strong> {print_request.document_name}</p>
            <p><strong>Status:</strong> 
                <span style="color: {status_color}; font-weight: bold;">
                    {new_status.replace('_', ' ').title()}
                </span>
            </p>
        </div>
"""
    
    if new_status == 'approved':
        html_body += '<div style="background: #d4edda; padding: 15px; margin: 20px 0; border-left: 4px solid #28a745;"><p style="margin: 0; color: #155724;">✓ Good news! Your request has been approved.</p></div>'
    elif new_status == 'rejected':
        html_body += f'<div style="background: #f8d7da; padding: 15px; margin: 20px 0; border-left: 4px solid #dc3545;"><p style="margin: 0; color: #721c24;">✗ Request rejected<br>Reason: {print_request.admin_notes or "No reason provided"}</p></div>'
    elif new_status == 'completed':
        html_body += '<div style="background: #d1ecf1; padding: 15px; margin: 20px 0; border-left: 4px solid #17a2b8;"><p style="margin: 0; color: #0c5460;">✓ Your print job is ready for pickup!</p></div>'
    
    html_body += f"""
        <h3>Details</h3>
        <ul>
            <li>Pages: {print_request.num_pages}</li>
            <li>Copies: {print_request.num_copies}</li>
            <li>Color: {'Yes' if print_request.color else 'No'}</li>
            <li>Double-sided: {'Yes' if print_request.double_sided else 'No'}</li>
        </ul>
        
        <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
            Thanks,<br>
            Print Request System
        </p>
    </div>
</body>
</html>
"""
    
    send_email(subject, [user.email], text_body, html_body)


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
