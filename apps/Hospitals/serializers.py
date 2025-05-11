from rest_framework import serializers
from .models import BloodRequest  
# from apps.blood_stock.models import BloodStock
from apps.Hospitals.models import HospitalProfile
from apps.city.models import City
from django.utils import  timezone
from datetime import timedelta
from constants import BLOOD_TYPES
from apps.donors.models import DonationRequest 
import re

from django.db.models import Count, Q

class BloodRequestSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='hospital.name', read_only=True)
    target_city_name = serializers.CharField(source='hospital.city', read_only=True)
    estimated_fulfillment_time = serializers.SerializerMethodField()
    blood_type_available = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = [
            'id',
            'hospital',
            'name',
            'blood_type',
            'blood_type_available',
            'quantity',
            'urgency',
            'status',
            # 'target_city',
            'target_city_name',
            'created_at',
            'estimated_fulfillment_time'
        ]
        extra_kwargs = {
            'hospital': {'write_only': True, 'required': False},
            'status': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def validate_blood_type(self, value):
        """Ensure valid blood type format"""
        valid_types = [choice[0] for choice in BLOOD_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid blood type. Must be one of: {', '.join(valid_types)}")
        return value

    def validate(self, data):
        blood_type = data.get('blood_type')
        quantity = data.get('quantity')
        current_time = timezone.now()
        
        if blood_type and quantity:
            # Get count of available units (not expired and available)
            available_units = DonationRequest.objects.filter(
                blood_type=blood_type,
                 status = '4'
            ).aggregate(
                total=Count('id', filter=Q(
                    expiration_date__gt=current_time
                ))
            )['total'] or 0
            
            if available_units < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {available_units} units available for blood type {blood_type}'
                })

        # Emergency requests validation
        if data.get('urgency') == 'immediate' and data.get('quantity') > 5:
            raise serializers.ValidationError({
                'quantity': 'Maximum 5 units for immediate requests'
            })
            
        return data

    def get_estimated_fulfillment_time(self, obj):
        """Calculate estimated fulfillment time based on urgency"""
        urgency_map = {
            'immediate': timedelta(minutes=30),
            'urgent': timedelta(hours=2),
            'normal': timedelta(hours=24)
        }
        if obj.status == '1':
            return (obj.created_at + urgency_map.get(obj.urgency, timedelta(hours=1))).isoformat()
        return None

    def get_blood_type_available(self, obj):
        """Get available quantity by counting valid, available records"""
        return DonationRequest.objects.filter(
            blood_type=obj.blood_type,
            status = '4'
        ).aggregate(
            total=Count('id', filter=Q(
                expiration_date__gt=timezone.now()
            ))
        )['total'] or 0

    def create(self, validated_data):
        """Custom creation with default status"""
        request = BloodRequest.objects.create(
            **validated_data,
            status='1'
        )
        return request