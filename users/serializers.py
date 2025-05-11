


# import re
# from django.db import transaction
# from rest_framework import serializers
# from users.models import User
# from apps.donors.models import Donor
# from apps.city.models import City
# from apps.Hospitals.models import HospitalProfile  # Import HospitalProfile

# class UserSerializer(serializers.ModelSerializer):
#     # Donor-specific fields (required only for donors)
#     national_id = serializers.CharField(required=False, write_only=True, allow_null=True)
#     name = serializers.CharField(required=False, write_only=True, allow_null=True)
#     phone_number = serializers.CharField(required=False, write_only=True, allow_null=True)
    
#     # Hospital-specific fields (required only for hospitals)
#     hospital_name = serializers.CharField(required=False, write_only=True, allow_null=True)
    
#     # Shared fields
#     city = serializers.PrimaryKeyRelatedField(
#         queryset=City.objects.all(),
#         required=True,
#         write_only=True
#     )

#     class Meta:
#         model = User
#         fields = [
#             'username', 'email', 'password', 'role',
#             'national_id', 'name', 'city', 'phone_number',  # Donor fields
#             'hospital_name',  # Hospital field
#         ]
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate_phone_number(self, value):
#         if value:  # Only validate if provided (donors)
#             pattern = r'^(010|011|012|015)\d{8}$'
#             if not re.match(pattern, value):
#                 raise serializers.ValidationError("Phone number must be a valid Egyptian number (e.g. 010xxxxxxxx).")
#             if Donor.objects.filter(phone_number=value).exists():
#                 raise serializers.ValidationError("A donor with this phone number already exists.")
#         return value
    
#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("A user with this email already exists.")
#         return value

#     def validate_national_id(self, value):
#         if value:  # Only validate if provided (donors)
#             if not re.match(r'^[23]\d{13}$', value):
#                 raise serializers.ValidationError("National ID must be 14 digits and start with 2 or 3.")
#             if Donor.objects.filter(national_id=value).exists():
#                 raise serializers.ValidationError("A donor with this national ID already exists.")
#         return value

#     def validate(self, attrs):
#         role = attrs.get('role')
        
#         if role == 'donor':
#             required_fields = ['national_id', 'name', 'phone_number']
#             missing_fields = [field for field in required_fields if not attrs.get(field)]
#             if missing_fields:
#                 raise serializers.ValidationError({
#                     "error": f"Donors must provide: {', '.join(missing_fields)}"
#                 })
                
#         elif role == 'hospital':
#             if not attrs.get('hospital_name'):
#                 raise serializers.ValidationError({
#                     "error": "Hospitals must provide a hospital_name"
#                 })
                
#         return attrs

#     @transaction.atomic
#     def create(self, validated_data):
#         role = validated_data.get('role')
        
#         # Extract donor-specific fields
#         national_id = validated_data.pop('national_id', None)
#         name = validated_data.pop('name', None)
#         phone_number = validated_data.pop('phone_number', None)
        
#         # Extract hospital-specific fields
#         hospital_name = validated_data.pop('hospital_name', None)
#         city = validated_data.pop('city')

#         # Create User
#         user = User.objects.create_user(**validated_data)

#         # Create profile based on role
#         if role == 'donor':
#             Donor.objects.create(
#                 user=user,
#                 national_id=national_id,
#                 name=name,
#                 city=city,
#                 phone_number=phone_number
#             )
#         elif role == 'hospital':
#             HospitalProfile.objects.create(
#                 user=user,
#                 hospital_name=hospital_name,
#                 city=city
#             )

#         return user




import re
import random
import string
from django.db import transaction
from rest_framework import serializers
from users.models import User
from apps.donors.models import Donor
from apps.city.models import City
from apps.Hospitals.models import HospitalProfile
from apps.blood_stock.models import BloodStockProfile

class UserSerializer(serializers.ModelSerializer):
    # Donor-specific fields
    national_id = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, write_only=True, allow_null=True)
    phone_number = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True)
    
    
    # Shared fields
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role',
            'national_id', 'name', 'city', 'phone_number',  # Donor fields
            'name',  # Hospital field
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True}  # Make username read-only since we'll generate it
        }

    def generate_random_username(self, base_name=None):
        """
        Generate a random username with optional base name.
        Format: {base_name}_{random_string} or user_{random_string}
        """
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        if base_name:
            # Clean the base name (remove special chars, spaces, etc.)
            clean_base = re.sub(r'[^a-zA-Z0-9]', '', base_name).lower()
            return f"{clean_base}_{random_str}"
        return f"user_{random_str}"

    def validate_phone_number(self, value):
        if value:  # Only validate if provided (donors)
            pattern = r'^(010|011|012|015)\d{8}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("Phone number must be a valid Egyptian number (e.g. 010xxxxxxxx).")
            if Donor.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("A donor with this phone number already exists.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_national_id(self, value):
        if value:  # Only validate if provided (donors)
            if not re.match(r'^[23]\d{13}$', value):
                raise serializers.ValidationError("National ID must be 14 digits and start with 2 or 3.")
            if Donor.objects.filter(national_id=value).exists():
                raise serializers.ValidationError("A donor with this national ID already exists.")
        return value

    def validate(self, attrs):
        role = attrs.get('role')
        
        if role == 'donor':
            required_fields = ['national_id', 'name', 'phone_number']
            missing_fields = [field for field in required_fields if not attrs.get(field)]
            if missing_fields:
                raise serializers.ValidationError({
                    "error": f"Donors must provide: {', '.join(missing_fields)}"
                })
                
        elif role == 'hospital':
            if not attrs.get('name'):
                raise serializers.ValidationError({
                    "error": "Hospitals must provide a hospital name"
                })
        elif role == 'bloodBank':
            if not attrs.get('name'):
                raise serializers.ValidationError({
                    "error": "bloodBanks must provide a bloodBank name"
                })
                
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.get('role')
        
        # Extract fields
        national_id = validated_data.pop('national_id', None)
        name = validated_data.pop('name', None)
        phone_number = validated_data.pop('phone_number', None)
        city = validated_data.pop('city')
        email = validated_data.get('email')

        # Generate username based on role
        if role == 'donor' and name:
            validated_data['username'] = self.generate_random_username(name)
        elif role == 'hospital' and name:
            validated_data['username'] = self.generate_random_username(name)
        
        elif role == 'bloodBank' and name:
            validated_data['username'] = self.generate_random_username(name)

        else:
            # Use email prefix or completely random if no suitable base
            email_prefix = email.split('@')[0] if email else None
            validated_data['username'] = self.generate_random_username(email_prefix)

        # Create User
        user = User.objects.create_user(**validated_data)

        # Create profile based on role
        if role == 'donor':
            Donor.objects.create(
                user=user,
                national_id=national_id,
                name=name,
                city=city,
                phone_number=phone_number
            )
        elif role == 'hospital':
            HospitalProfile.objects.create(
                user=user,
                name=name,
                city=city
            )
        elif role == 'bloodBank':
            # Add blood bank profile creation if needed

            print()
            print()
            print("name")
            print(name)
            print()
            print()
            print()
            BloodStockProfile.objects.create(
                user=user,
                name=name,
                city=city
            )
            pass

        return user