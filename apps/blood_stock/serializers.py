from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.city.models import City
from .models import BloodStockProfile

User = get_user_model()

class BloodStockProfileSerializer(serializers.ModelSerializer):
    # Nested serializers for related fields
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    
    # Expanded fields (optional)
    user_details = serializers.SerializerMethodField(read_only=True)
    city_details = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = BloodStockProfile
        fields = [
            'id',
            'user',
            'user_details',
            'name',
            'city',
            'city_details',
            'city_name',
            # Add any other fields you want to include
        ]
        extra_kwargs = {
            'user': {'write_only': True},  # Hide user details in write operations
        }
    
    def get_user_details(self, obj):
        """Return basic user info"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email
        }
    
    def get_city_details(self, obj):
        """Return basic city info"""
        return {
            'id': obj.city.id,
            'name': obj.city.name,
            # Add other city fields as needed
        }
    
    def create(self, validated_data):
        """Handle creation with related objects"""
        # Get or create user if needed
        user = validated_data.pop('user')
        city = validated_data.pop('city')
        
        blood_stock = BloodStockProfile.objects.create(
            user=user,
            city=city,
            **validated_data
        )
        return blood_stock
    
    def update(self, instance, validated_data):
        """Handle updates with related objects"""
        user = validated_data.pop('user', None)
        city = validated_data.pop('city', None)
        
        if user:
            instance.user = user
        if city:
            instance.city = city
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance