from django import template

register = template.Library()

@register.filter
def hide_email(email):
    parts = email.split('@')
    if len(parts) == 2:
        username, domain = parts
        hidden_username = username[0] + '*' * (len(username) - 1)
        return f"{hidden_username}@{domain}"
    return email
