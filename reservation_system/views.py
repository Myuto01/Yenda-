from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUserForm, LoginForm, TripScheduleForm
from .models import TripSchedule, ReservationSystemUser, Ticket
from app.models import User
import decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group


@unauthenticated_user
def register(request):
    print("loading")
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # Save the User instance first
            user = form.save(commit=False)
            user.save()

            # Create a ReservationSystemUser instance associated with the newly created user
            reservation_user = ReservationSystemUser.objects.create(user=user, email=form.cleaned_data.get('email'))

            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='Bus Operator')
            user.groups.add(group)

            # Log in the user after successful registration
            login(request, user)

            messages.success(request, f'Welcome, {user.username}! Your account has been successfully created.')
            return redirect('reservation_system:bus_operator_dashboard')
        else:
            # Print form errors to help identify the issue
            print(form.errors)

    context = {'form': form}
    return render(request, '../templates/bus_operator_register.html', context)

@unauthenticated_user
def login_register(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)
        print(username)
        print(password)
        if user is not None:
            login(request, user)
            return redirect('reservation_system:bus_operator_dashboard')
        else:
            messages.info(request, 'Username or Password is incorrect')

    return render(request, '../templates/bus_operator_login.html', {'form': form})



@allowed_users(allowed_roles=['Bus Operator'])
def bus_operator_dashboard(request):
    context = {'user': request.user}
    return render(request, '../templates/bus_operator_dashboard.html', context)


@allowed_users(allowed_roles=['Bus Operator'])
def detail_entry(request):
    form = TripScheduleForm()
    if request.method == 'POST':
        form = TripScheduleForm(request.POST)
        if form.is_valid():
            bus_operator = get_object_or_404(User, id=request.user.id)
            form.instance.bus_operator = bus_operator
             # Retrieve the original price
            price = form.cleaned_data['price']

            # Calculate the 5% increase
            new_price = price * decimal.Decimal('1.05')

            # Assign the increased price back to the form
            form.instance.price = new_price

            trip_schedule = form.save()

            # Assuming you want to create seats associated with the TripSchedule
            #create_seats(trip_schedule)

            messages.success(request, 'Trip schedule added successfully.')
            return redirect('reservation_system:detail-entry')

    context = {'form': form}
    return render(request, 'detail_entry.html', context)

#QR code Scanner
def qr_code_scanner(request):
    context = {}
    return render(request, 'qr_code_scanner.html', context)


#QR Code scanner verification 
def verify_ticket(request):
    if request.method == 'POST':
        ticket_code = request.POST.get('code')
        try:
            ticket = Ticket.objects.get(ticket_no=ticket_code)
            if ticket.confirmed:
                return JsonResponse({'valid': True, 'message': 'Ticket is valid'})
            else:
                return JsonResponse({'valid': False, 'message': 'Ticket is not confirmed'})
        except Ticket.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Ticket not found'})
    return JsonResponse({'error': 'Invalid request method'})









"""
def create_seats(trip_schedule):
    for row in range(1, trip_schedule.rows + 1):
        for column in range(1, trip_schedule.columns + 1):
            seat_number = f"{row}-{column}"
            Seat.objects.create(trip_schedule=trip_schedule, seat_number=seat_number, row=row, column=column)
"""