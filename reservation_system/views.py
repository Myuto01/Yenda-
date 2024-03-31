from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUserForm, LoginForm, TripScheduleForm
from .models import TripSchedule, ReservationSystemUser, Ticket
from app.models import User
import decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group
from django.http import JsonResponse

#Django Rest Framework imports
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from json import JSONDecodeError
from reservation_system.serializers import BusOperatorRegistrationSerializer,TripScheduleSerializer
from rest_framework.parsers import JSONParser
from rest_framework import views, status
from rest_framework.response import Response

@unauthenticated_user
def register(request):
    context = {}
    return render(request, '../templates/bus_operator_register.html', context)

# User Registration serializer
class BusOperatorRegistrationAPIView(views.APIView):
    """
    A simple APIView for creating application users.
    """
    serializer_class = BusOperatorRegistrationSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request):
            data = JSONParser().parse(request)
            print('Executed')
            serializer = BusOperatorRegistrationSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                
                group = Group.objects.get(name='Bus Operator')
                user.groups.add(group)

                login(request, user)
                return Response(serializer.data, status=200)
            else:
                errors = serializer.errors
                print('Errors:',serializer.errors)  
                print('Redirecting')
                return JsonResponse({'errors': errors}, status=400)  # Return JSON response with status code 400
        




@allowed_users(allowed_roles=['Bus Operator'])
def bus_operator_dashboard(request):
    context = {'user': request.user}
    return render(request, '../templates/bus_operator_dashboard.html', context)

# User Registration serializer
class TripScheduleAPIView(views.APIView):
    """
    A simple APIView for creating application users.
    """
    serializer_class = TripScheduleSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request):
        data = JSONParser().parse(request)
        print('Executed')
        serializer = TripScheduleSerializer(data=data)
        if serializer.is_valid():
            # Get the bus operator
            bus_operator = get_object_or_404(User, id=request.user.id)
            # Set the bus operator for the instance
            serializer.validated_data['bus_operator'] = bus_operator
            
            # Calculate the new price
            price = serializer.validated_data['price']
            new_price = price * decimal.Decimal('1.05')
            # Assign the increased price back to the serializer
            serializer.validated_data['price'] = new_price
            
            # Save the serializer instance
            trip_schedule = serializer.save()
            
            return Response(serializer.data, status=200)
        else:
            errors = serializer.errors
            print('Errors:',serializer.errors)  
            print('Redirecting')
            return JsonResponse({'errors': errors}, status=400)  # Return JSON response with status code 400

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