from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .customAuthentication import authenticate

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    # permission_classes = [AllowAny]
    def post(self,request):
    # if request method is post request
        try:
            data = request.data
            
        except:
             return Response({"error":"data must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        # initialize errors object
        errors = {}
        # check if data key not sent
        if not data :
            
            return Response({"error":"data must be provided"}, status=status.HTTP_400_BAD_REQUEST)
       
        # check if key email not sent
        elif "email" not in data.keys():
            
            return Response({"error":"email must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        # check if key password not sent
        elif "password" not in data.keys():
            
            return Response({"error":"password must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(email=data["email"],password=data["password"],status="1")
    
        # if it's exists
        if user:

            obj = {
                "email":user.email,
           
                "id":user.id,
                "role":user.role,
                
             
            }
            obj["tokens"] = user.tokens()
            return Response({"user": obj}, status=status.HTTP_200_OK)
            
        else:

            return Response({"error":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)