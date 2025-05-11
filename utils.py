# blood_stock/utils.py
from geopy.distance import geodesic

def calculate_distance(request, stock):
    """Calculate distance between request city and stock city in km"""
    return geodesic(
        (request.target_city.latitude, request.target_city.longitude),
        (stock.city.latitude, stock.city.longitude)
    ).km