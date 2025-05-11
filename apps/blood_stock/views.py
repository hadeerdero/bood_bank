from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from apps.blood_stock.services import fulfill_requests_optimally
from rest_framework.decorators import api_view
from django.db.models import Q
from .models import BloodStockProfile


@api_view(["GET"])
def getStocksData(request):
        id = request.GET.get('id')
        q_objects = Q() 
        if id:
            q_objects &= Q(id=id)
       
        stocks = BloodStockProfile.objects.filter(q_objects).values("id","city__name","name")
        return Response(stocks, status=status.HTTP_200_OK)

class ProcessRequestsView(APIView):
    """API endpoint to manually trigger request processing"""
    def post(self, request):
        fulfill_requests_optimally()
        return Response(
            {"status": "Request processing completed"},
            status=status.HTTP_200_OK
        )