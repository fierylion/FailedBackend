# q: I want to authenticate all api's that are not /login or /register
import jwt
from django.conf import settings
from rest_framework import status
from django.http import  JsonResponse
from .models import User
import re
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
User = get_user_model()
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.path)
        # q: create a regex to mathc /api/v1/company and api/v1/company/..... and /api/v1/package
        pattern = r'^/api/v1/(company(/.*)?|package)$'
        if re.match(pattern, request.path):
            try:
                token = request.headers.get('Authorization', None)
                if token:
                    token = token.split(' ')[1]
                    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
                    user = User.objects.get(username=payload['username'])
                    request.user = user
                else:
                    return JsonResponse({'success': False, 'msg': 'You are Unauthorized!!'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return JsonResponse({'success': False, 'msg': 'You are Unauthorized!!'}, status=status.HTTP_401_UNAUTHORIZED)

        response = self.get_response(request)
        return response
class PackageAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.path.startswith('api/v1/company'):
            #check if the hasnt made any subscription at all
            package_created_at = request.user.package_created_at
            default_datetime = datetime(2002, 1, 1, 0, 0,0)  # Set default datetime to January 1st of the current year at 2002
            if(package_created_at == default_datetime):
                return Response({'success': True, 'message': 'Please choose a package', status: status.HTTP_403_FORBIDDEN})
            #check if it hasnt expired if expired only get method is allowed
            if(package_created_at + datetime.timedelta(days=30)< datetime.now() and request.method !='get'):
                return Response({'success': False, 'message': 'Package has expired','expired': True, 'status': status.HTTP_403_FORBIDDEN})
        response = self.get_response(request)
        return response

