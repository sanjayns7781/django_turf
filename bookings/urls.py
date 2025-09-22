from django.urls import path
from .views import (
    confirm_booking,
    verify_booking,
    advanced_search,
    cancel_booking,
    bulk_booking,
    booking_stats,
    get_booking_locations,
    get_available_slots,
    get_booking_by_date,
    booking_actions,
    book_turf
)

urlpatterns = [
    path('',book_turf),
    path('<int:id>/',booking_actions),
    path('by-date/<int:date>/',get_booking_by_date),
    path('bookings/available-slots/',get_available_slots),
    path('by-location/<str:location>/',get_booking_locations),
    path('stats/>',booking_stats),
    path('bulk-create/',bulk_booking),
    path('bulk-cancel/>',cancel_booking),
    path('advanced-search/',advanced_search),
    path('verify/<str:booking_code>',verify_booking),
    path('<int:id>/confirm/',confirm_booking)
]
