from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer , UpdateProfileSerializer

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
    if request.method == "PUT":
        serializer = UpdateProfileSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    if request.method == "GET":
        serializer = UpdateProfileSerializer(request.user)
        return Response(serializer.data)
    
        

