from geopy.distance import geodesic
from django.db.models import F, Q
from django.utils import timezone
from apps.Hospitals.models import BloodRequest
# from apps.blood_stock.models import BloodStock
from django.db import transaction

# def fulfill_requests_optimally():
    
#     """Process pending requests considering distance and urgency"""
#     pending_requests = BloodRequest.objects.filter(
#         status='Pending'
#     ).select_related('hospital', 'target_city')
    
#     print()
#     print()
#     print()
#     print()
#     print("pending_requests")
#     print(pending_requests)
#     print()
#     print()
#     print()
#     print()


#     for request in pending_requests:
#         # Find matching blood stock with distance calculation
#         matching_stocks = BloodStock.objects.filter(
#             Q(blood_type=request.blood_type) &
#             Q(quantity__gte=request.quantity) &
#             Q(expiration_date__gt=timezone.now())
#         ).annotate(
#             distance=geodesic(
#                 (request.target_city.latitude, request.target_city.longitude),
#                 (F('city__latitude'), F('city__longitude'))
#             )
#         ).order_by('distance', 'expiration_date')
        
#         print()
#         print()
#         print()
#         print()
#         print("matching_stocks")
#         print(matching_stocks)
#         print()
#         print()
#         print()
#         print()

#         if matching_stocks.exists():
#             stock = matching_stocks.first()
#             fulfill_request(request, stock)

from geopy.distance import geodesic
from django.utils import timezone
from django.db.models import Q
from apps.donors.models import DonationRequest

def fulfill_requests_optimally():
    """Process pending requests considering distance and urgency"""
    pending_requests = BloodRequest.objects.filter(
        status='1'
    ).select_related('hospital', 'city')

    print("\n\npending_requests:", pending_requests, "\n\n")

    for request in pending_requests:
        try:
            # First get all potential matching stocks
            potential_stocks = DonationRequest.objects.filter(
                Q(blood_type=request.blood_type) &
                Q(quantity__gte=request.quantity) &
                Q(expiration_date__gt=timezone.now())
            ).select_related('city')  # Important for performance

            # Calculate distance for each stock and create a list of tuples (distance, stock)
            stocks_with_distance = []
            target_lat = float(request.target_city.latitude)
            target_lon = float(request.target_city.longitude)
            
            for stock in potential_stocks:
                try:
                    stock_lat = float(stock.city.latitude)
                    stock_lon = float(stock.city.longitude)
                    distance = geodesic(
                        (target_lat, target_lon),
                        (stock_lat, stock_lon)
                    ).km
                except (TypeError, ValueError, AttributeError):
                    # If coordinates are invalid, set distance to infinity (will sort last)
                    distance = float('inf')
                
                stocks_with_distance.append((distance, stock))

            # Sort by distance then by expiration date
            stocks_with_distance.sort(key=lambda x: (x[0], x[1].expiration_date))
            
            print("\n\nmatching_stocks (sorted by distance):")
            for dist, stock in stocks_with_distance:
                print(f"Distance: {dist:.2f} km | Stock ID: {stock.id} | Expires: {stock.expiration_date}")
            print("\n\n")

            # Fulfill the request with the closest available stock
            if stocks_with_distance:
                closest_stock = stocks_with_distance[0][1]
                fulfill_request(request, closest_stock)

        except Exception as e:
            print(f"Error processing request {request.id}: {str(e)}")
            continue
        
def fulfill_request(request, stock):
   
    """Atomic fulfillment of a single request"""
    with transaction.atomic():
        # Lock the stock record
        locked_stock = DonationRequest.objects.select_for_update().get(pk=stock.pk)
        
        if locked_stock.quantity >= request.quantity:
            locked_stock.quantity -= request.quantity
            locked_stock.save()
            
            request.status = 'fulfilled'
            request.save()
          
            return True
        else:
                # Reject if no stock available
                request.status = 'rejected'
                request.save()
    return False