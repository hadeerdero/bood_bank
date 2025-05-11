from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.http import Http404
from .models import Donor, DonationRequest
from .serializers import DonationSerializer
from users.models import User
from django.conf import settings
from apps.blood_stock.models import BloodStockProfile
from rest_framework.viewsets import ViewSet
from rest_framework import generics, status
from .serializers import DonationRequestSerializer, DonationRequestTestResultSerializer, DonationRequestCompletionSerializer


class DonateView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        rejection_reason = ''
        if user.role != 'donor':
            return Response({"error": "Only donors can donate blood."}, status=status.HTTP_403_FORBIDDEN)

        try:
            donor = Donor.objects.get(user=user)
        except Donor.DoesNotExist:
            return Response({"error": "Donor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # try:
        #     blood_stock = BloodStockProfile.objects.get(id=request.data.blood_stock)
        # except BloodStockProfile.DoesNotExist:
        #     return Response({"error": "Blood stock profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the latest donation by this donor
        last_donation = DonationRequest.objects.filter(donor=donor).order_by('-donation_date').first()
        if last_donation:
            if (datetime.now().date() - last_donation.donation_date).days < 90:
                rejection_reason = "Donation rejected: Less than 3 months since last donation."
                self.send_rejection_email(user.email, rejection_reason)
                return Response({"error": "Donation not allowed: Less than 3 months since last donation."}, status=400)

        # Check virus test result
        # virus_test_result = request.data.get('virus_test_result')
        # if virus_test_result in ['true', 'True', True, '1', 1]:
        #     rejection_reason = "Donation rejected: Virus test failed."
        #     self.send_rejection_email(user.email, rejection_reason)
        #     return Response({"error": "Donation rejected: Virus test failed."}, status=400)

        # Passed all checks: Save donation
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            donation = serializer.save(
                donor=donor,
            )
            return Response({"message": "Donation accepted."}, status=201)
        return Response(serializer.errors, status=400)

    def send_rejection_email(self, email, reason):
        send_mail(
            subject='Blood Donation Rejection',
            message=reason,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

# class DonationRequestView(ViewSet):

#     def list(self, request):

#         requests = DonationRequest.objects.filter(q_objects).exclude(status=4).order_by("-updated_at")
#         return Response(requests, status=status.HTTP_200_OK)
       

class DonationRequestView(ViewSet):
    def get_object(self, pk):
        try:
            return DonationRequest.objects.get(pk=pk)
        except DonationRequest.DoesNotExist:
            raise Http404
        
    # def testDonationRequest(self, request, *args, **kwargs):


       

    #     try:
    #         request_id = kwargs.get('pk') 
    #         Dorequest = DonationRequest.objects.get(id=request_id)
    #     except DonationRequest.DoesNotExist:
    #         return Response({"error": "Donation Request not found."}, status=status.HTTP_404_NOT_FOUND)
        
    #      # Check virus test result
    #     virus_test_result = request.data.get('virus_test_result')
    #     if virus_test_result in ['true', 'True', True, '1', 1]:
    #         rejection_reason = "Donation rejected: Virus test failed."
    #         DonateView.send_rejection_email(Dorequest.donor.user.email, rejection_reason)
    #         return Response({"error": "Donation rejected: Virus test failed."}, status=400)
        
    #     serializer = DonationRequestSerializer(Dorequest, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        # Get all donation requests excluding status=4 (rejected), ordered by most recently updated
        queryset = DonationRequest.objects.select_related(
            'donor',
            'donor__city',
            'blood_stock',
            'blood_stock__city'
        ).exclude(status='4').order_by("-updated_at")
        
        # Apply any filters from query parameters
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        blood_type_filter = request.query_params.get('blood_type', None)
        if blood_type_filter:
            queryset = queryset.filter(blood_type=blood_type_filter)
        
     
        
        # Serialize all results if no pagination
        serializer = DonationRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class TestDonationRequestView(APIView):
    def patch(self, request, pk, format=None):
        try:
            donation_request = DonationRequest.objects.get(id=pk)
        except DonationRequest.DoesNotExist:
            return Response(
                {"error": "Donation Request not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = DonationRequestTestResultSerializer(
            donation_request, 
            data=request.data,
            partial=True  # Allow partial updates
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CompleteDonationRequestView(generics.UpdateAPIView):
    queryset = DonationRequest.objects.all()
    serializer_class = DonationRequestCompletionSerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verify the request is in tested status
        if instance.status != '2':
            return Response(
                {"error": "Only tested requests can be completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # Force status to completed (3)
        validated_data = serializer.validated_data
        validated_data['status'] = '3'
        
        self.perform_update(serializer)
        
        return Response(serializer.data)