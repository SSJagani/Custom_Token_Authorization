from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import *


# Create your views here.
class LoginView(APIView):
    def post(self, request):
        print(request.data)
        serializers = LoginSerializers(data=request.data)
        if serializers.is_valid():
            print('if conditions')
        else:
            qry_message = {
                'status': False,
                'message': 'Some other error occurred!',
                'data': serializers.errors
            }
            return Response(qry_message, status=status.HTTP_200_OK)
