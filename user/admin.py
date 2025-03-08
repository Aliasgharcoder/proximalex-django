from django.contrib import admin
from oauth2_provider.models import Application, AccessToken, Grant, RefreshToken
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Replace with your custom user model

# Register the custom user model
admin.site.register(CustomUser, UserAdmin)
# admin.site.register(Application)
# admin.site.register(AccessToken)
# admin.site.register(Grant)
# admin.site.register(RefreshToken)
# Register your models here.



