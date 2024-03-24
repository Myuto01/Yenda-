# serializers.py
from rest_framework import serializers
from . models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class BusOperatorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'error_messages': {'required': 'Password is required'}},
            'email': {'error_messages': {'unique': 'Email is already taken'}},
            'username': {'error_messages': {'unique': 'Username is already taken'}}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match"})
        return data

    def save(self):
        password = self.validated_data['password']
        account = User.objects.create(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        account.set_password(password)
        account.save()
        return account