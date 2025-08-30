from django.contrib import admin
from .models import *


from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

class CustomUserAdmin(DefaultUserAdmin):
    # Show only these fields in the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'is_staff'),
        }),
    )

    # Show only these fields in the edit form
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username', 'email', 'password', 'is_staff')}),
    )

    # Columns to display in user list
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff')

    # Make email the unique identifier
    ordering = ('username',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ExamAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'exam', 'is_used', 'valid_until', 'created_at')
    list_filter = ('is_used', 'valid_until', 'exam')

admin.site.register(Exam)
admin.site.register(ExamAccessToken, ExamAccessTokenAdmin)
