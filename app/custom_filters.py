from django import template

register = template.Library()

@register.filter
def format_time(time):
    # Ensure that the time is in the format HH:MM
    return time.strftime('%I:%M %p') if time else ''
