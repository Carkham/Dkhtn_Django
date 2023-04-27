from django.contrib import admin
from .models import User


class UserManager(admin.ModelAdmin):
    list_display = ['id', 'username', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'date_joined']
    list_display_links = ['id']
    search_fields = ['username']


admin.site.register(User, UserManager)
