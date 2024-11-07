from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class TurfOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to a User model
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name



class Turf(models.Model):
    TURF_CHOICES = [
        ('5s', '5s'),
        ('7s', '7s'),
        ('11s', '11s'),
    ]

    turffname = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    turf_type = models.CharField(max_length=10, choices=TURF_CHOICES)  # Updated this line
    phone_number = models.CharField(max_length=15)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey('TurfOwner', on_delete=models.CASCADE, related_name='turfs')

    def __str__(self):
        return self.turffname
    
class Booking(models.Model):
    user_name = models.CharField(max_length=255, verbose_name="User Name")  # User's name
    user_phone = models.CharField(max_length=15, verbose_name="User Phone Number")  # User's phone number
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='bookings')  # Link to the turf being booked
    booking_date = models.DateField(verbose_name="Booking Date")  # Date of the booking
    start_time = models.TimeField(verbose_name="Start Time")  # Start time for booking
    end_time = models.TimeField(verbose_name="End Time")  # End time for booking

    def save(self, *args, **kwargs):
        # Ensure the end time is at least one hour after the start time
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(self.booking_date, self.start_time)
            end_datetime = datetime.combine(self.booking_date, self.end_time)
            if (end_datetime - start_datetime).total_seconds() < 3600:  # Less than 1 hour
                raise ValueError("The booking must be for at least 1 hour.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.turf} by {self.user_name} on {self.booking_date}"