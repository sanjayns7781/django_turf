from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import BookingSerializer,UpdateBookingSerializer
from .models import TurfBooking
from .pagination import BookingPagination
from .permissions import IsAdmin,IsAdminOrOwner
from django.db.models import Q,Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.utils.timezone import now


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
    
@api_view(["PUT","GET","DELETE"])
@permission_classes([IsAuthenticated])
def booking_actions(request,booking_id):
    if request.method == "GET":
        try:
            booking = TurfBooking.objects.get(id=booking_id)
        except TurfBooking.DoesNotExist:
            return Response("No booking found under this id",status=404)
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data,status=200)
    
    elif request.method == "PUT":
        try:
            booking = TurfBooking.objects.get(id=booking_id)
        except TurfBooking.DoesNotExist:
            return Response("No booking found under this id",status=404)
        
        serializer = UpdateBookingSerializer(booking,request.data, partial=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)

        pass
    elif request.method == "DELETE":
        try:
            booking = TurfBooking.objects.get(id=booking_id)
        except TurfBooking.DoesNotExist:
            return Response("No booking found under this id",status=404)
        
        role = request.user.role.name
        if role in ["ADMIN","OWNER"] or (role == "CUSTOMER" and booking.user == request.user):
            booking.delete()
            return Response("Has successfully deleted",status=204)
        return Response("Only admins and owner can delete booking")

        
# Task 8: Advanced Booking Queries 
# GET /api/bookings/by-date/{date}/

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_by_date(request,date):
    # Validate and parse date
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    bookings = TurfBooking.objects.filter(booking_date=parsed_date)
    if not bookings.exists():
        return Response({"message": "No bookings found on this date."}, status=404)
    
    serializer = BookingSerializer(bookings,many=True)
    return Response(serializer.data,status=200)

# GET /api/bookings/available-slots/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_slots(request):
    date = request.query_params.get("date")
    location = request.query_params.get("location")

    if not date:
        return Response({"error": "date is required"}, status=400)
    
    # 1. All possible slots (from model choices)
    # all_slots = [slot[0] for slot in TurfBooking._meta.get_field('time_slot').choices]
    all_slots = [slot[0] for slot in TurfBooking.TIME_SLOTS]

    # 2. Filter bookings for that date (and location if provided)
    filters = {"booking_date": date}
    if location:
        filters["location__icontains"] = location

    bookings = TurfBooking.objects.filter(**filters)

    # 3. Extract booked slots
    booked_slots = [
        {"time_slot": b.time_slot, "turf_name": b.turf_name}
        for b in bookings
    ]

    booked_slot_times = [b.time_slot for b in bookings]

    # 4. Available = All - Booked
    available_slots = [slot for slot in all_slots if slot not in booked_slot_times]

    return Response(
        {
            "date":date,
            "available_slots":available_slots,
            "booked_slots":booked_slots
            
        },
        status=200
    )


# GET /api/bookings/by-location/{location}/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_locations(request,location):
    bookings = TurfBooking.objects.filter(location__icontains = location)
    serializer = BookingSerializer(bookings,many=True)
    return Response(serializer.data,status=200)


# Task 9: Booking Statistics (Admin/Owner Only)
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminOrOwner])
def booking_stats(request):
    bookings = TurfBooking.objects.all()

    # get the total number of booking
    total_bookings = TurfBooking.objects.count()

    # 2. Bookings this month
    today = now().date()
    bookings_this_month = TurfBooking.objects.filter(
    booking_date__year=today.year,
    booking_date__month=today.month
    ).count()

    # 3. Popular time slots
    popular_time_slots = (
        TurfBooking.objects.values("time_slot")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # 4. Popular locations
    popular_locations = (
        TurfBooking.objects.values("location")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # 5. Popular turfs
    popular_turfs = (
        TurfBooking.objects.values("turf_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:3]
    )

    # 6. Bookings by month
    bookings_by_month = (
        TurfBooking.objects
        .annotate(month=TruncMonth("booking_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    
    bookings_by_month = [
        {"month": b["month"].strftime("%B %Y"), "count": b["count"]}
        for b in bookings_by_month
    ]

    return Response({
        "total_bookings": total_bookings,
        "bookings_this_month": bookings_this_month,
        "popular_time_slots": list(popular_time_slots),
        "popular_locations": list(popular_locations),
        "popular_turfs": list(popular_turfs),
        "bookings_by_month": bookings_by_month
    }, status=200)