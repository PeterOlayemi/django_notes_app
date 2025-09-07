from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def short_timesince(value):
    if not value:
        return ""
    delta = now() - value
    if delta.days > 0:
        return f"{delta.days}d ago"
    seconds = delta.seconds
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    return f"{seconds // 3600}h ago"
