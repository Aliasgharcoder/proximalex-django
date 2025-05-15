from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Case,CustomUser

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # for confirmation

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2','role')
        extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2',None)
        user = User.objects.create_user(**validated_data)
        return user

class CaseSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=False, allow_null=True)
    lawyer_details = serializers.SerializerMethodField()  # Enhanced lawyer info
    urgency_level = serializers.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        required=True
    )
    class Meta:
        model = Case
        fields = '__all__'
        extra_kwargs = {
            'client': {'read_only': True},
            'lawyer': {'read_only': False},
            'status': {'read_only': True},
        }
        
    def get_lawyer_details(self, obj):
        if not obj.lawyer:
            return None
        return {
            'id': obj.lawyer.id,
            'name': f"{obj.lawyer.first_name} {obj.lawyer.last_name}",
            'specialization': obj.lawyer.specialization,
            'sub_specialization': obj.lawyer.sub_specialization,
            'success_rate': obj.lawyer.success_rate,
            'hourly_rate': obj.lawyer.hourly_rate
        }
        
    def validate(self, data):
         # Add validation for all required fields
        required_fields = ['title', 'description', 'category', 'location']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required."})
        return data
    def validate_urgency_level(self, value):
        return value.lower()  # Convert to lowercase
class LawyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'specialization','location']