# blood_stock/urls.py
from django.urls import path
from .views import ProcessRequestsView, getStocksData

urlpatterns = [
    path(
        'process-blood-requests/',
        ProcessRequestsView.as_view(),
        name='process-blood-requests'
    ),
     path('', getStocksData, name='get-stocks'),
]