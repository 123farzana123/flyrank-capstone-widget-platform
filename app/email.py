def send_confirmation_email(submission_data: dict) -> None:
    """
    Fake email side-effect — logs to console instead of real SMTP.
    Deliberately allowed to fail (or be forced to fail, for testing)
    without affecting the caller: the submission must succeed either way.
    """
    print(f"[EMAIL] Confirmation would be sent for submission: {submission_data}")
    