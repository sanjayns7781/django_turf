from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer , UpdateProfileSerializer , UserManagementSerializer, RoleSerializer
from .permissions import IsAdminOrOwner,IsAdmin
from rest_framework.permissions import IsAuthenticated
from .models import User, Role
from .pagination import UserPagination
from django.db.models import Q

@api_view(['POST'])
@permission_classes([])  # allow anyone
def register(request):
    serializer = RegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data,status=200)
    return Response(serializer.errors,status=400)

@api_view(['PUT','GET'])
@permission_classes([])
def get_profile(request):
    print("hi iam coming into the view")
    if request.method == "PUT":
        serializer = UpdateProfileSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    if request.method == "GET":
        serializer = UpdateProfileSerializer(request.user)
        return Response(serializer.data)


# User Management (Admin/Owner Only)
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminOrOwner])
def list_users(request):
    users = User.objects.all()

    # filtering based on role
    role = request.query_params.get('role')
    if role:
        users = users.filter(role__name=role.upper())

    # filtering based on the isactive status
    is_active = request.query_params.get('is_active')
    if is_active:
        users = users.filter(is_active=is_active.lower()=='true')

    # searching
    search = request.query_params.get('search')
    if search:
        users = users.filter(
            Q(username_icontains=search)|
            Q(email_icontains=search)|
            Q(phone_number_icontains=search)
        )

    # Pagination part
    paginator = UserPagination()
    result_page = paginator.paginate_queryset(users,request)
    serializer = UserManagementSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PUT','GET','DELETE'])
@permission_classes([IsAuthenticated,IsAdminOrOwner])
def manage_user(request,user_id):
    try:
        user = User.objects.get(id = user_id)
    except User.DoesNotExist:
        return Response({"error":"user does not found"},status=404)
    
    if request.method == "GET":
        serializer = UserManagementSerializer(user)
        return Response(serializer.data,status=200)
    
    if request.method == "PUT":
        serializer = UserManagementSerializer(user, request.data, partial=True, context ={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdmin])
def disable_user(request,user_id):
    try:
        user = User.objects.get(id = user_id)
    except User.DoesNotExist:
        return Response({"error":"user does not found"},status=404)
    
    user.is_active = False
    user.save()
    serializer = UserManagementSerializer(user)
    return Response(serializer.data,status=200)

    
# Task 6: Role Management (Admin Only)
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated,IsAdmin])
def get_or_create_roles(request):
    if request.method == "GET":
        roles = Role.objects.all()
        serializer = RoleSerializer(roles,many=True)
        return Response(serializer.data,status=200)
    
    if request.method == "POST":
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
