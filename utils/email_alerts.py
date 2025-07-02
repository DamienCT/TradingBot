"""
email_alerts.py

Stub function to send daily update email. 
"""
def send_daily_update_email(email_config, subject, body, attachments=None):
    print("[EMAIL] Sending daily update to:", email_config["recipient"])
    print("Subject:", subject)
    print("Body:", body)
    # Not actually sending anything yet
    if attachments:
        print("Attachments:", attachments)
    # Stub done
