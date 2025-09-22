from rest_framework import serializers
from .models import TurfBooking
import string,random

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfBooking
        fields = ['id', 'booking_code', 'turf_name', 'location', 'booking_date', 'time_slot']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        booking_code = validated_data.get('booking_code')
        if booking_code:
            if TurfBooking.objects.filter(booking_code=booking_code).exists():
                raise serializers.ValidationError({"booking_code": "This booking code already exists."})
        else:
            while True:
                booking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not TurfBooking.objects.filter(booking_code=booking_code).exists():
                    break
            validated_data["booking_code"] = booking_code
        validated_data["user"] = user
        

        if TurfBooking.objects.filter(
            turf_name=validated_data['turf_name'],
            booking_date=validated_data['booking_date'],
            time_slot=validated_data['time_slot']
        ).exists():
            raise serializers.ValidationError("This turf is already booked for the given time slot.")

        return super().create(validated_data)
    
class UpdateBookingSerializer(serializers.ModelSerializer):
    # time_slot = serializers.ChoiceField(choices=TurfBooking.TIME_SLOTS)

    class Meta:
        model = TurfBooking
        fields = ['turf_name', 'location', 'booking_date', 'time_slot']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user

        if user.role.name == "CUSTOMER" and instance.user != user:
            raise serializers.ValidationError("Customers can not edit the booking")
        return super().update(instance, validated_data)
# This class overide the default ListSserializer
class BulkBookingSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        booking = []
        request = self.context.get('request')
        user = request.user

        for bookings in validated_data:
            booking_code = bookings.get('booking_code')
            if booking_code:
                if TurfBooking.objects.filter(booking_code=booking_code).exists():
                    raise serializers.ValidationError({"booking_code": "This booking code already exists."})
            else:
                while True:
                    booking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not TurfBooking.objects.filter(booking_code=booking_code).exists():
                        break
                    bookings["booking_code"] = booking_code
            bookings['user'] = user

            if TurfBooking.objects.filter(
            turf_name=bookings['turf_name'],
            booking_date=bookings['booking_date'],
            time_slot=bookings['time_slot']
            ).exists():
                raise serializers.ValidationError("This turf is already booked for the given time slot.")
            
            # collecting the objects to memmory so that we need to hit DB only once
            booking.append(TurfBooking(**bookings))

        return TurfBooking.objects.bulk_create(booking)
    
class BulkBookingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfBooking
        fields = ['turf_name', 'location', 'booking_date', 'time_slot', 'booking_code']
        list_serializer_class = BulkBookingSerializer


class VerifyBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfBooking
        fields = ["booking_code","turf_name","location","booking_date","time_slot","customer_name","status"]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["customer_name"] = instance.user.name
        data["status"] = "confirmed"
        return data