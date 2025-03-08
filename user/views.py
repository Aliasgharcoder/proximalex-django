from rest_framework import generics
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout

User = get_user_model()

class CollectUsernameView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the social auth user (if it exists)
        try:
            social_auth = UserSocialAuth.objects.get(uid=request.session.get('social_auth_uid'))
        except ObjectDoesNotExist:
            return Response({'error': 'Social auth not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update the user
        user, created = User.objects.get_or_create(
            email=social_auth.uid,  # Use email or other unique identifier
            defaults={'username': username}
        )

        # Associate the social auth with the user
        social_auth.user = user
        social_auth.save()

        # Log the user in
        from django.contrib.auth import login
        login(request, user)

        return Response({'message': 'Username set successfully'}, status=status.HTTP_200_OK)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer



# class LogoutView(APIView):
#     def post(self, request):
#         try:
#             refresh_token = request.data['refresh_token']
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response(status=204)
#         except Exception as e:
#             return Response(status=400)    
class LogoutView(APIView):
    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Log the user out (for session-based authentication)
            logout(request)

            return Response(
                {'message': 'Logged out successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )