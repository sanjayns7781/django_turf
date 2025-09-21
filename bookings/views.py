from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import BookingSerializer
from .models import TurfBooking
from .pagination import BookingPagination
from django.db.models import Q


# Task 7: Turf Booking CRUD Operations
@api_view(['POST',"GET"])
@permission_classes([IsAuthenticated])
def book_turf(request):
    if request.method == "POST":
        serializer = BookingSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
    
    if request.method == "GET":
        bookings = TurfBooking.objects.all()
        turf_name = request.query_params.get('turf_name')

        if request.user.role.name == "CUSTOMER":
            bookings = bookings.filter(user=request.user) 

        if turf_name:
            bookings = bookings.filter(turf_name__icontains=turf_name)

        location = request.query_params.get('location')
        if location:
            bookings = bookings.filter(location__icontains=location)

        booking_date = request.query_params.get('booking_date')
        if booking_date:
            bookings = bookings.filter(booking_date=booking_date)

        time_slot = request.query_params.get('time_slot')
        if time_slot:
            bookings = bookings.filter(time_slot=time_slot)

        user_id = request.query_params.get('user_id')
        if user_id and request.user.role.name in ["ADMIN","OWNER"]:
            bookings = bookings.filter(user__id=user_id)
        
        search = request.query_params.get('search')
        if search:
            bookings = bookings.filter(
                Q(booking_code__icontains=search)|
                Q(turf_name__icontains=search)|
                Q(location__icontains=search)
            )
        
        ordering = request.query_params.get('ordering')
        if ordering:
            bookings = bookings.order_by(ordering)

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if date_from and date_to:
            bookings = bookings.filter(booking_date__range=[date_from,date_to])
        elif date_from:
            bookings = bookings.filter(booking_date__gte=date_from)
        elif date_to:
            bookings = bookings.filter(booking_date__lte=date_to)

        paginator = BookingPagination()
        result_page = paginator.paginate_queryset(bookings,request)
        serializer = BookingSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)

