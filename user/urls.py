from django.urls import path
from user.views import UserRegistrationView,LoginView, LogoutView,CollectUsernameView,google_login_redirect,CaseViewSet,LawyerListAPIView,predict_lawyers_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
case_list = CaseViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

case_detail = CaseViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path('users/',UserRegistrationView.as_view(), name='register'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('collect_username', CollectUsernameView.as_view(), name='collect_username'),
    path('google-redirect/', google_login_redirect, name='google-redirect'),
    path('cases/', case_list, name='case-list'),
    path('cases/<int:pk>/', case_detail, name='case-detail'),
    path('lawyers-list/', LawyerListAPIView.as_view(), name='lawyer-list'),
    path('predict-lawyers/', predict_lawyers_view, name='predict-lawyers'),

]

# print("Registered URL patterns:", urlpatterns)