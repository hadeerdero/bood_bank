from django.urls import path
from .views import CityView, getCitiesData

urlpatterns = [
    path('create', CityView.as_view({'post': 'post'}), name='city-create'),
    path('update/<int:pk>', CityView.as_view({'put': 'put'}), name='city-update'),
    path('', getCitiesData, name='get-city-details'),
  
    
]
