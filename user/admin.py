from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Case

# ============ Custom Admin for CustomUser ============

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # What columns to show in the list view
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'role', 'specialization', 'experience_years', 
        'location', 'is_available', 'is_staff'
    )

    # What fields to filter by (on the right side)
    list_filter = ('role', 'location', 'specialization', 'is_available', 'is_staff', 'is_superuser')

    # What fields to search
    search_fields = ('username', 'email', 'first_name', 'last_name', 'specialization', 'location')

    # Organizing fields when editing/creating a user
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'role', 'phone_number', 'specialization', 'experience_years', 
                'location', 'languages_spoken', 'bio', 'is_available'
            )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': (
                'role', 'phone_number', 'specialization', 'experience_years', 
                'location', 'languages_spoken', 'bio', 'is_available'
            )
        }),
    )

# ============ Custom Admin for Case ============

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    actions = ['mark_as_high_urgency']
    
    def mark_as_high_urgency(self, request, queryset):
        queryset.update(urgency_level='high')
    mark_as_high_urgency.short_description = "Mark selected cases as high urgency"
    model = Case
    
    # What columns to show in list view
    list_display = (
        'title', 'client', 'lawyer', 'category', 
        'location', 'urgency_level', 'status', 'created_at'
    )

    # What fields to filter by
    list_filter = ('urgency_level', 'status', 'category', 'location', 'created_at')

    # What fields to search
    search_fields = ('title', 'description', 'client__username', 'lawyer__username', 'category', 'location')

    # Ordering
    ordering = ('-created_at',)
