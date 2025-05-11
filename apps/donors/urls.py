from django.urls import path
from .views import DonateView, DonationRequestView, TestDonationRequestView, CompleteDonationRequestView

urlpatterns = [
    path('donate/', DonateView.as_view(), name='donate-blood'),
     path('', DonationRequestView.as_view({'get': 'list'}), name='donate-blood'),
      path('update/<int:pk>', DonationRequestView.as_view({'put': 'testDonationRequest'}), name='update-request'),

       path(
        'donation-requests/<int:pk>', 
        TestDonationRequestView.as_view(), 
        name='test-donation-request'
    ),
    path(
        'donation-requests/<int:pk>/complete/',
        CompleteDonationRequestView.as_view(),
        name='complete-donation-request'
    ),
]
