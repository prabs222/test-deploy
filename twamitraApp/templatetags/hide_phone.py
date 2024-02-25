from django import template

register = template.Library()

@register.filter
def hide_phone(phone):
    if phone and len(phone) >= 6:  
        visible_part = phone[:3]
        hidden_part = '*' * (len(phone) - 3)
        return f"{visible_part}{hidden_part}"
    return phone
