from django.urls import path
from .views import BloodRequestCreateView

urlpatterns = [
    path(
        'blood-requests/', 
        BloodRequestCreateView.as_view(),
        name='blood-request-create'
    ),
]