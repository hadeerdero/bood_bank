from rest_framework import generics, status
from rest_framework.response import Response
from .models import BloodRequest
from .serializers import BloodRequestSerializer

class BloodRequestCreateView(generics.CreateAPIView):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer

    def perform_create(self, serializer):
        hospital = self.request.user.hospitalprofile
        serializer.save(hospital=hospital)