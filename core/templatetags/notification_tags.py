# core/templatetags/notification_tags.py

from django import template
from core.models import Notification

register = template.Library()

@register.simple_tag
def unread_notification_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(user=user, is_read=False).count()
    return 0
