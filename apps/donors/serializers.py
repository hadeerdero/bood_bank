from rest_framework import serializers
from .models import DonationRequest
# from apps.donors.serializers import D

from rest_framework import serializers
from users.models import User  # Import your User model
from apps.city.models import City  # Import your City model
from .models import Donor
from apps.blood_stock.serializers import BloodStockProfileSerializer
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}  # Never include password in responses
        }

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']  # Adjust fields based on your City model

class DonorSerializer(serializers.ModelSerializer):
    # Nested serializers for related fields
    user = UserSerializer()
    city = CitySerializer()
    
    # Computed fields (if needed)
    full_name = serializers.SerializerMethodField()
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = Donor
        fields = [
            'id',
            'user',
            'name',
            'full_name',
            'national_id',
            'phone_number',
            'city',
            'city_name',
            # Add any other fields you want to include
        ]
        extra_kwargs = {
            'national_id': {'read_only': True}  # Typically national_id shouldn't change
        }
    
    def get_full_name(self, obj):
        """Combine user's first and last name if available, fallback to donor name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.name
    
    def create(self, validated_data):
        """Handle nested user creation"""
        user_data = validated_data.pop('user')
        city_data = validated_data.pop('city', None)
        
        # Create User first
        user = User.objects.create_user(**user_data)
        
        # Create Donor
        donor = Donor.objects.create(user=user, **validated_data)
        
        return donor
    
    def update(self, instance, validated_data):
        """Handle nested updates"""
        user_data = validated_data.pop('user', {})
        city_data = validated_data.pop('city', None)
        
        # Update User
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update Donor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
        
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = ['blood_type', 'virus_test_result','note',"blood_stock"]


class DonationRequestSerializer(serializers.ModelSerializer):
    donor = DonorSerializer()
    blood_stock = BloodStockProfileSerializer()
    
    class Meta:
        model = DonationRequest
        fields = '__all__'

# serializers.py
from rest_framework import serializers
from .models import DonationRequest
from django.core.mail import send_mail
from django.conf import settings

class DonationRequestTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = ['expiration_date', 'status', 'virus_test_result']
    
    def update(self, instance, validated_data):
        # Get the original test result before update
        original_test_result = instance.virus_test_result
        new_test_result = validated_data.get('virus_test_result', instance.virus_test_result)
        
        # Update the instance
        instance.expiration_date = validated_data.get('expiration_date', instance.expiration_date)
        instance.status = validated_data.get('status', instance.status)
        instance.virus_test_result = new_test_result
        instance.save()
        
        # Send email if test result changed from positive to negative
        if original_test_result != new_test_result and not new_test_result:
            self.send_test_denied_email(instance)
            
        return instance
    
    def send_test_denied_email(self, donation_request):
        subject = 'Blood Donation Test Results'
        message = f"""
        Dear {donation_request.donor.name},
        
        We regret to inform you that your recent blood donation test results were positive.
        Please contact us for more information.
        
        Donation ID: {donation_request.id}
        Test Date: {donation_request.updated_at}
        
        Sincerely,
        Blood Bank Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [donation_request.donor.user.email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )


# class DonationRequestCompletionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DonationRequest
#         fields = ['blood_type', 'donation_date', 'note', 'quantity', 'status']
#         extra_kwargs = {
#             'status': {'read_only': True}  # We'll set this in the view
#         }

#     def validate(self, data):
#         """
#         Validate that the quantity is within acceptable range
#         and donation date is not in the past
#         """
#         if data.get('quantity', 0) < 100 or data.get('quantity', 0) > 500:
#             raise serializers.ValidationError(
#                 "Quantity must be between 100ml and 500ml"
#             )
        
#         if data.get('donation_date') < timezone.now().date():
#             raise serializers.ValidationError(
#                 "Donation date cannot be in the past"
#             )
            
#         return data


# serializers.py
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import DonationRequest

class DonationRequestCompletionSerializer(serializers.ModelSerializer):
    donation_date = serializers.DateField(input_formats=['%Y-%m-%d'])  # Explicit date format
    
    class Meta:
        model = DonationRequest
        fields = ['blood_type', 'donation_date', 'note', 'quantity', 'status']
        extra_kwargs = {
            'status': {'read_only': True},
            'blood_type': {'required': True},
            'quantity': {'required': True},
            'donation_date': {'required': True}
        }

    def validate(self, data):
        """
        Validate donation completion data
        """
        # Validate quantity
        if data['quantity'] < 100 or data['quantity'] > 500:
            raise serializers.ValidationError({
                'quantity': 'Must be between 100ml and 500ml'
            })
        
        # Validate donation date is not in past
        if data['donation_date'] < timezone.now().date():
            raise serializers.ValidationError({
                'donation_date': 'Cannot be in the past'
            })
            
        return data