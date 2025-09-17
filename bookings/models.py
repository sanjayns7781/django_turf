from django.db import models
from accounts.models import User

# Create your models here.
class TurfBooking(models.Model):
    booking_code = models.CharField(unique=True,max_length=8)
    turf_name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    booking_date = models.DateField()
    TIME_SLOTS = [
        ('06:00-08:00', '06:00-08:00'),
        ('08:00-10:00', '08:00-10:00'),
        ('10:00-12:00', '10:00-12:00'),
        ('12:00-14:00', '12:00-14:00'),
        ('14:00-16:00', '14:00-16:00'),
        ('16:00-18:00', '16:00-18:00'),
        ('18:00-20:00', '18:00-20:00'),
        ('20:00-22:00', '20:00-22:00'),
    ]
    time_slot = models.CharField(max_length=50,choices=TIME_SLOTS)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "turf_db"