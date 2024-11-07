# turff_App/views.py

from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from .forms import *
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count


def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            # Check if user exists and is a superuser
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            elif user is not None and not user.is_superuser:
                messages.error(request, 'Access denied: Admin privileges are required.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'admin_login.html', context)

@login_required
def admin_dashboard(request):
    # Fetch total bookings, total turfs
    total_bookings = Booking.objects.count()
    total_turfs = Turf.objects.count()

    # Fetch bookings count by turf (used in pie chart)
    turfs = Turf.objects.annotate(booking_count=Count('bookings')).all()

    # Fetch upcoming bookings for the table
    bookings = Booking.objects.all().order_by('booking_date')[:10]  # Limiting to the top 10 bookings

    context = {
        'total_bookings': total_bookings,
        'total_turfs': total_turfs,
        'turfs': turfs,
        'bookings': bookings,
    }

    return render(request, 'admin_dashboard.html', context)

def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')

def register_turf_owner(request):
    if request.method == 'POST':
        form = TurfOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a TurfOwner instance
            TurfOwner.objects.create(user=user, name=user.username, phone_number=form.cleaned_data['phone_number'])
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login_turf_owner')
    else:
        form = TurfOwnerRegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'register_turf_owner.html', context)

def login_turf_owner(request):
    if request.method == 'POST':
        form = TurfOwnerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('turf_owner_dashboard')  # Redirect to a home page or dashboard
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = TurfOwnerLoginForm()

    context = {
        'form': form
    }
    return render(request, 'login_turf_owner.html', context)


from django.contrib.auth import logout
def custom_logout(request):
    logout(request)  # Logs out the user
    return redirect('/')  # Redirect to the login page or any other page you want

from .decorators import custom_login_required

@custom_login_required
def turf_owner_dashboard(request):
    # Get the TurfOwner instance for the logged-in user
    owner = TurfOwner.objects.get(user=request.user)  
    # Get all turfs owned by the owner
    turfs = Turf.objects.filter(owner=owner)  
    # Get all bookings for the owner's turfs
    bookings = Booking.objects.filter(turf__owner=owner)  

    # Check if a date filter is applied
    filter_date = request.GET.get('date')
    if filter_date:
        try:
            # Convert the filter_date to a date object
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            # Filter bookings by the selected date
            bookings = bookings.filter(booking_date=filter_date)
        except ValueError:
            # Handle the case where the date conversion fails
            bookings = bookings  # Keep all bookings if the date is invalid

    context = {
        'turfs': turfs,
        'bookings': bookings,
    }
    return render(request, 'turf_owner_dashboard.html', context)

def cancel_booking(request, booking_id):
    # Get the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the current user is the owner of the turf
    if request.user == booking.turf.owner.user:
        booking.delete()  # Delete the booking
        return redirect('turf_owner_dashboard')  # Redirect to the dashboard after cancellation

    # If not authorized, redirect back to the dashboard (or handle appropriately)
    return redirect('turf_owner_dashboard')


# turff_App/views.py
@custom_login_required
def add_turf(request):
    if request.method == 'POST':
        form = TurfForm(request.POST)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.owner = TurfOwner.objects.get(user=request.user)  # Set the turf owner to the logged-in user
            turf.save()
            return redirect('turf_owner_dashboard')  # Redirect to the dashboard after adding
    else:
        form = TurfForm()

    return render(request, 'add_turf.html', {'form': form})

def home(request):
    form = TurfSearchForm(request.GET or None)
    results = None
    locations = Turf.objects.values_list('location', flat=True).distinct()  # Get unique locations

    # Manually get location from GET request, as we're removing it from the form
    location = request.GET.get('location')
    turf_type = form.cleaned_data.get('turf_type') if form.is_valid() else None

    # Filter turfs based on user inputs
    queryset = Turf.objects.all()
    
    if location:
        queryset = queryset.filter(location__icontains=location)
    if turf_type:
        queryset = queryset.filter(turf_type=turf_type)

    results = queryset

    context = {
        'form': form,
        'results': results,
        'locations': locations,  # Pass locations to template
    }
    return render(request, 'home.html', context)


from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from xhtml2pdf import pisa  # Ensure xhtml2pdf is installed
from .models import Turf, Booking

def book_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    message = None
    available_slots = []
    booking_date = None

    # Calculate available slots if a date is provided in GET
    if 'date' in request.GET:
        booking_date_str = request.GET.get('date')
        
        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            existing_bookings = Booking.objects.filter(turf=turf, booking_date=booking_date).order_by('start_time')

            # Define operating hours (assuming 8 AM - 10 PM)
            opening_time = datetime.combine(booking_date, datetime.strptime("08:00", "%H:%M").time())
            closing_time = datetime.combine(booking_date, datetime.strptime("22:00", "%H:%M").time())

            # Calculate available slots
            start_time = opening_time
            for booking in existing_bookings:
                end_time = datetime.combine(booking_date, booking.start_time)
                if start_time < end_time:
                    available_slots.append((start_time.time(), end_time.time()))
                start_time = datetime.combine(booking_date, booking.end_time)

            # Add final slot if there's time before closing
            if start_time < closing_time:
                available_slots.append((start_time.time(), closing_time.time()))

        except ValueError:
            message = "Invalid date format. Please select a valid date."

    # Handle booking submission
    if request.method == 'POST':
        # Ensure booking_date is available
        if not booking_date:
            booking_date_str = request.POST.get('booking_date')
            try:
                booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            except ValueError:
                message = "Invalid booking date. Please select a valid date."

        start_time_str = request.POST.get('start_time')
        duration_str = request.POST.get('duration')  # Duration in hours (1-5)
        user_name = request.POST.get('user_name')
        user_phone = request.POST.get('user_phone')

        # Validate start time and duration
        if not start_time_str or not duration_str:
            message = "Please provide both start time and duration."
            return render(request, 'book_turf.html', {
                'turf': turf,
                'message': message,
                'available_slots': available_slots,
                'booking_date': booking_date,
            })

        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            duration = int(duration_str)
            if duration < 1 or duration > 5:
                message = "Please select a duration between 1 and 5 hours."
                return render(request, 'book_turf.html', {
                    'turf': turf,
                    'message': message,
                    'available_slots': available_slots,
                    'booking_date': booking_date,
                })

            # If booking is for today, ensure start time is in the future
            if booking_date == datetime.today().date():
                current_time = datetime.now().time()
                if start_time <= current_time:
                    message = "You cannot book a time in the past."
                    return render(request, 'book_turf.html', {
                        'turf': turf,
                        'message': message,
                        'available_slots': available_slots,
                        'booking_date': booking_date,
                    })

            # Calculate end time based on duration
            start_datetime = datetime.combine(booking_date, start_time)
            end_datetime = start_datetime + timedelta(hours=duration)
            end_time = end_datetime.time()

            # Check if booking exceeds closing time
            if end_datetime > datetime.combine(booking_date, closing_time.time()):
                message = "The selected duration exceeds the turf's closing time."
                return render(request, 'book_turf.html', {
                    'turf': turf,
                    'message': message,
                    'available_slots': available_slots,
                    'booking_date': booking_date,
                })

            # Check for conflicting bookings
            existing_bookings = Booking.objects.filter(turf=turf, booking_date=booking_date)
            for booking in existing_bookings:
                if not (end_time <= booking.start_time or start_time >= booking.end_time):
                    message = "The selected time slot is already booked."
                    return render(request, 'book_turf.html', {
                        'turf': turf,
                        'message': message,
                        'available_slots': available_slots,
                        'booking_date': booking_date,
                    })

            # Calculate booking price
            total_price = Decimal(duration) * turf.price  # Assuming turf has a price field

            # Create booking instance
            booking = Booking.objects.create(
                turf=turf,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                user_name=user_name,
                user_phone=user_phone,
            )

            # Generate PDF slip after successful booking
            return generate_pdf_slip(booking, total_price)

        except ValueError:
            message = "Please provide a valid start time and duration."

    context = {
        'turf': turf,
        'message': message,
        'available_slots': available_slots,
        'booking_date': booking_date,
    }
    return render(request, 'book_turf.html', context)

def generate_pdf_slip(booking, total_price):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_slip_{booking.id}.pdf"'
    html_content = render_to_string('booking_slip.html', {'booking': booking, 'total_price': total_price})
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('There was an error generating the PDF. Please try again.')
    return response
