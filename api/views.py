from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Company, Package
from .serializers import UserSerializer, CompanySerializer, PackageSerializer
import jwt
from django.conf import settings
from datetime import datetime
# Create your views here.
def home(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['POST'])
def register(request):
    #check for field package and replace with object package
    data = request.data
    package = data.get('package', None)
    if(package is None):
        package = 'free'
    if( package and isinstance(package, str)   and package in  ('free', 'business', 'professional')):
        package = Package.objects.get(type=package)
        data['package'] = package
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success':True, 'data':serializer.data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'msg': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    data = request.data
    username = data.get('username', None)
    password = data.get('password', None)
    if(email and password):
        user = User.objects.filter(username = username).first()
        if user:
            #q: I want to check password
            if user.check_password(password, user.password):
                serializer = UserSerializer(user)
                # Create token
                token = jwt.encode({"username": serializer.data.username},
                                   settings.JWT_SECRET, algorithm='HS256')
                return Response({'success': True, 'data': serializer.data, 'token': token}, status=status.HTTP_200_OK)
            return Response({'success': False, 'msg': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': False, 'msg': 'Invalid username'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': False, 'msg': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
def validate_company_id(compId):
    if is_valid_uuid(compId):
        company = Company.objects.filter(id=compId).first()
        if company:
            return True
    return False

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def company(request, id=None):
    logged_user= request.user['username']
    user = User.objects.get(username=logged_user)
    if(id and not validate_company_id(id)):
        return Response({'success': False, 'msg': 'Invalid company id'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        if id:
            company = Company.objects.get(id=id)
            serializer = CompanySerializer(company)

            return Response({'success': True, 'data': {'company':serializer.data, 'user': {'username': user.username, 'package': user.package.type} }}, status=status.HTTP_200_OK)
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response({'success': True, 'data': {'companies':serializer.data, 'user': {'username': user.username, 'package': user.package.type} }}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        data_post = request.data
        data_post['user'] = user
        serializer = CompanySerializer(data=data_post)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        company = Company.objects.get(id=id)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'success': False, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        company = Company.objects.get(id=id)
        company.delete()
        return Response({'success': True, 'data': 'Company deleted successfully'}, status=status.HTTP_200_OK)


# transfarring from one package to another, get request to know which package currently own
@api_view(['GET', 'POST'])
def view_upgrade_package(request):
    logged_user= request.user['username']
    user = User.objects.get(username=logged_user)
    if request.method == 'GET':
        return Response({'success': True, 'data': {'package': user.package.type} }, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        data_post = request.data
        package = data_post.get('package', None)
        if( package and isinstance(package, str)   and package in  ('free', 'business', 'professional')):
            package = Package.objects.get(type=package)
            user.package = package
            user.package_created_at = datetime.now()
            user.save()
            return Response({'success': True, 'data': {'package': user.package.type} }, status=status.HTTP_200_OK)
        return Response({'success': False, 'msg': 'Invalid package'}, status=status.HTTP_400_BAD_REQUEST)
