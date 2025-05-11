from .models import User
from django.db.models import Q

def authenticate(email=None, password=None, status=None):
    try:
        # search User model for email for this user with incoming email
        user = User.objects.get(Q(email=email))
        passwordValid = user.check_password(password)
        if passwordValid:
                     
            return user
       
        else:
            return None
       
    except User.DoesNotExist:
        return None
