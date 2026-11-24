from django.contrib import admin
from .models import EventCategory, EventRegistration, EventAttendance, Events
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Users

# Register your models here.

admin.site.register(Events)
admin.site.register(EventCategory)
admin.site.register(EventRegistration)
admin.site.register(EventAttendance)


@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        (_('Custom Fields'), {'fields': ('role', 'roll_no', 'department')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Custom Fields'), {'fields': ('email', 'role', 'roll_no', 'department')}),
    )