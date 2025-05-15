from rest_framework import generics,serializers
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework import viewsets, permissions
from .models import Case
from .serializers import CaseSerializer
from user.lawyer_matcher.predict_lawyer import predict_best_lawyers
User = get_user_model()
from rest_framework.generics import ListAPIView
from .models import CustomUser
from .serializers import LawyerSerializer
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)
def google_login_redirect(request):
    user = request.user

    if user.is_authenticated:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # redirect to your React app with tokens
        frontend_url = f"http://localhost:5173/?access={access_token}&refresh={refresh_token}"
        return redirect(frontend_url)
    else:
        return redirect("http://localhost:5173/login")  
      
class CollectUsernameView(APIView):
    def get(self, request):
        # Optional: this handles accidental GET requests gracefully
        return Response({'message': 'Please send a POST request with a username.'}, status=405)

    def post(self, request,*args, **kwargs):
        username = request.data.get('username',None)
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the user's social auth using session
        try:
            social_auth = UserSocialAuth.objects.get(uid=request.session.get('social_auth_uid'))
        except ObjectDoesNotExist:
            return Response({'error': 'Social auth not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get the user using their email
        user, created = User.objects.get_or_create(
            email=social_auth.extra_data.get('email'),
            defaults={'username': username}
        )

        # Associate the social auth with the user
        social_auth.user = user
        social_auth.save()

        # Log the user in
        login(request, user)

        return Response({'message': 'Username set successfully'}, status=status.HTTP_200_OK)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]



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
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Case.objects.filter(client=user)
        elif user.role == 'lawyer':
            return Case.objects.filter(lawyer=user)
        return Case.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'client':
            raise permissions.PermissionDenied("Only clients can create cases.")

        case_data = {
            'case_type': self.request.data.get('category'),
            'case_subtype': self.request.data.get('sub_category', 'general'),
            'location': self.request.data.get('location'),
            'urgency': self.request.data.get('urgency_level', 'medium').lower(),
            'complexity': self.request.data.get('complexity', 'moderate').lower(),
            'max_hourly_rate': self.request.data.get('max_hourly_rate')
        }

        selected_lawyer_id = self.request.data.get('selectedLawyer')
        if selected_lawyer_id:
            try:
                selected_lawyer = CustomUser.objects.get(
                    id=selected_lawyer_id, 
                    role='lawyer',
                    is_available=True
                )
                serializer.save(client=user, lawyer=selected_lawyer)
                return
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    {"selectedLawyer": "Selected lawyer not found or not available."}
                )

        # Auto-match lawyers if none selected
        matched_lawyers = predict_best_lawyers(case_data)
        if not matched_lawyers:
            raise serializers.ValidationError(
                {"non_field_errors": ["No suitable lawyers found. Please try adjusting your criteria or select a lawyer manually."]}
            )
        
        # Get the first lawyer from matched results
        best_lawyer,best_score = matched_lawyers[0] if matched_lawyers else None
        if best_lawyer:
            serializer.save(client=user, lawyer=best_lawyer)
        else:
            raise serializers.ValidationError(
                {"non_field_errors": ["Failed to assign a lawyer. Please try again."]}
            )

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            document = request.FILES.get('document')
            
            if document:
                data['document'] = document

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
    
            case = serializer.instance
            headers = self.get_success_headers(serializer.data)
    
            response_data = {
                "case": serializer.data,
                "message": "Case created successfully"
            }
            
            if hasattr(case, 'lawyer') and case.lawyer:
                response_data["lawyer"] = {
                    "id": case.lawyer.id,
                    "username": case.lawyer.username,
                    "specialization": case.lawyer.specialization,
                }
    
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        
        except Exception as e:
            print(f"Error creating case: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_lawyers_view(request):
    try:
        data = request.data
        
        # Prepare case data with proper defaults and validation
        case_data = {
            'case_type': data.get('case_type', 'unknown'),
            'case_subtype': data.get('case_subtype', 'general'),
            'location': data.get('location', 'unknown'),
            'urgency': data.get('urgency', 'medium').lower(),
            'complexity': data.get('complexity', 'moderate').lower(),
            'max_hourly_rate': int(data['max_hourly_rate']) if data.get('max_hourly_rate') else None
        }

        # Get matched lawyers
        matched_lawyers = predict_best_lawyers(case_data, top_n=3)
        
        # Prepare response
        if not matched_lawyers:
            return Response({'matches': [], 'message': 'No matching lawyers found'}, status=200)
        
        return Response({
            'matches': [
                {
                    'id': lawyer.id,
                    'username': lawyer.username,
                    'specialization': lawyer.specialization,
                    'success_rate': lawyer.success_rate,
                    'hourly_rate': lawyer.hourly_rate,
                    'location': lawyer.location,
                    'experience_years': lawyer.experience_years,
                    'match_score': float(score)  # Handle case where score isn't attached
                }
                for lawyer,score in matched_lawyers
            ]
        })
    
    except ValueError as e:
        return Response({'error': f"Invalid input data: {str(e)}"}, status=400)
    except Exception as e:
        print(f"Error in predict_lawyers_view: {str(e)}")
        return Response({'error': "An error occurred while finding lawyers"}, status=500)
class LawyerListAPIView(ListAPIView):
    queryset = CustomUser.objects.filter(is_available=True, role='lawyer')
    serializer_class = LawyerSerializer
    permission_classes = [AllowAny]                      