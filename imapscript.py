import imaplib
import email
from email.header import decode_header

def decode_subject(header):
    """
    Decode email subject
    """
    decoded = decode_header(header)
    subject = []
    for part, encoding in decoded:
        if isinstance(part, bytes):
            if encoding is not None:
                part = part.decode(encoding)
            subject.append(part)
    return ''.join(subject)

def email_exists(target_conn, email_message):
    """
    Check if an email exists on the target server
    """
    # Search for email on target server
    result, data = target_conn.search(None, "ALL")
    if result == 'OK':
        for num in data[0].split():
            result, raw_email = target_conn.fetch(num, "(RFC822)")
            if result == 'OK':
                target_email_message = email.message_from_bytes(raw_email[0][1])
                if target_email_message['Message-ID'] == email_message['Message-ID']:
                    return True
    return False

def migrate_emails(source_host, source_username, source_password, target_host, target_username, target_password):
    """
    Migrate emails from source IMAP server to target IMAP server
    """
    # Connect to source IMAP server
    source_conn = imaplib.IMAP4_SSL(source_host)
    source_conn.login(source_username, source_password)
    source_conn.select("INBOX")  # Select the mailbox to migrate

    # Connect to target IMAP server
    target_conn = imaplib.IMAP4_SSL(target_host)
    target_conn.login(target_username, target_password)
    target_conn.select("INBOX")  # Select the mailbox to migrate

    # Search for all emails in source mailbox
    result, data = source_conn.search(None, "ALL")
    if result == 'OK':
        for num in data[0].split():
            result, raw_email = source_conn.fetch(num, "(RFC822)")
            if result == 'OK':
                email_message = email.message_from_bytes(raw_email[0][1])
                if not email_exists(target_conn, email_message):
                    # Move email to target mailbox
                    target_conn.append("INBOX", None, None, raw_email[0][1])
                    print(f"Migrated email: {decode_subject(email_message['Subject'])}")
                else:
                    print(f"Skipped duplicate email: {decode_subject(email_message['Subject'])}")

    # Close connections
    source_conn.close()
    source_conn.logout()
    target_conn.close()
    target_conn.logout()

# Example usage You can change the details below to meet your needs
source_host = 'imap.domain.com'
source_username = 'email@domain.co.ug'
source_password = 'your_source_password'
target_host = 'mail.domain.com'
target_username = 'email@domain.co.ug'
target_password = 'your_taget_password'

migrate_emails(source_host, source_username, source_password, target_host, target_username, target_password)

