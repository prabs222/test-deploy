from django import template

register = template.Library()

@register.filter
def get_last_message(thread):
    return thread.messages.order_by('-timestamp').first()
