from rest_framework import serializers
from .models import User, Contact
from datetime import date
import re


# userserialzer to convert the data from one object to another object (python object to json and vice versa)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'


    def validate_email(self, value):
        # Email format validation
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Enter a valid email address.')
        return value
    

    def create(self, validated_data):
        user = User.objects.create_user( 
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
    


# Contactserialzer to convert the data from one object to another object (python object to json and vice versa)
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

    def validate_phone_no(self, value):
        pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Phone number must be entered in the format: "+91"')
        return value
    
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
