# serializers.py
from rest_framework import serializers
from . models import User, TripSchedule, BuyerDetails
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

    
class TripScheduleSerializer(serializers.ModelSerializer):
        class Meta:
            model = TripSchedule
            fields = [
                'driver',
                'origin',
                'destination',
                'departure_date',
                'departure_time',
                'estimated_arrival_time',
                'price',
            ]
        def validate(self, data):
            errors = {}
        
            # Check if driver is missing
            if 'driver' not in data or not data['driver']:
                errors['driver'] = ['Driver name is required.']
            
            # Check if origin is missing
            if 'origin' not in data or not data['origin']:
                errors['origin'] = ['Origin is required.']
            
            # Check if destination is missing
            if 'destination' not in data or not data['destination']:
                errors['destination'] = ['Destination is required.']
            
            # Check if departure_date is missing
            if 'departure_date' not in data or not data['departure_date']:
                errors['departure_date'] = ['Departure date is required.']
            
            # Check if departure_time is missing
            if 'departure_time' not in data or not data['departure_time']:
                errors['departure_time'] = ['Departure time is required.']
            
            # Check if estimated_arrival_time is missing
            if 'estimated_arrival_time' not in data or not data['estimated_arrival_time']:
                errors['estimated_arrival_time'] = ['Estimated arrival time is required.']
            
            # Check if price is missing
            if 'price' not in data:
                errors['price'] = ['Price is required.']

            if errors:
                raise serializers.ValidationError(errors)

            return data
