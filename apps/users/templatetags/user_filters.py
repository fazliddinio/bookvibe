from django import template
import re

register = template.Library()


@register.filter
def mask_email_username(username):
    """
    Mask email-based usernames for privacy.
    If username looks like an email, show only first 4 characters followed by asterisks.
    Otherwise, return the username as is.
    """
    if not username:
        return username

    # Check if the username looks like an email (contains @ and has email-like structure)
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(email_pattern, username):
        # It's an email, mask it
        if len(username) <= 4:
            return "*" * len(username)
        else:
            return username[:4] + "*" * (len(username) - 4)

    # Not an email, return as is
    return username


@register.filter
def is_email_username(username):
    """
    Check if a username looks like an email address.
    """
    if not username:
        return False

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, username))
