from django.contrib import admin

# Register your models here.
from .models import Wishlist, Notification

admin.site.register(Wishlist)
admin.site.register(Notification)