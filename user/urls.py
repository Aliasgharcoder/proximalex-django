from django.urls import path
from user.views import UserRegistrationView, LogoutView, CollectUsernameView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('users/',UserRegistrationView.as_view(), name='register'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('collect-username/', CollectUsernameView.as_view(), name='collect_username'),
]

print("Registered URL patterns:", urlpatterns)