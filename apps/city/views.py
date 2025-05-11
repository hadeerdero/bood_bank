from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import City 
from .serializers import CitySerializer
from django.db.models import Q
from rest_framework.viewsets import ViewSet
from django.db import transaction
from rest_framework.decorators import api_view

@api_view(["GET"])
def getCitiesData(request):
        id = request.GET.get('id')
        q_objects = Q() 
        if id:
            q_objects &= Q(id=id)
       
        cities = City.objects.filter(q_objects).values()
        return Response(cities, status=status.HTTP_200_OK)

class CityView(ViewSet):

    def get_object(self, pk):
        try:
            return City.objects.get(pk=pk)
        except City.DoesNotExist:
            raise Http404
    
    def post(self, request, *args, **kwargs):
        
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            city_id = kwargs.get('pk') 
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"error": "City not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    
   