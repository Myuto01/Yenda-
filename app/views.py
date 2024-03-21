from django.shortcuts import render, redirect,reverse, get_object_or_404
from .forms import CreateUserForm, LoginForm, SearchForm, BuyerDetailsForm, SelectTicketsForm, CourierSearchForm, PackageDetailsForm, ChangeNameForm, ChangeProfilePic, SuggestionForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from reservation_system.decorators import unauthenticated_user, allowed_users
from reservation_system.forms import MessageForm, PackagePaymentForm, CustomerServiceMessageForm, TicketConfirmationForm
from .models import User
from reservation_system.models import ReservationSystemUser, TripSchedule, BuyerDetails, Ticket, PackageDetails,  Message, PackagePayment, CustomerService
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseBadRequest
from datetime import datetime
import datetime
from django.forms import inlineformset_factory
import qrcode
import random
import string
import base64
from io import BytesIO
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.core.files.base import ContentFile
from django.utils.html import escape
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from requests import post  
from app.airtel_money.airtel_pay import AirtelPay
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.core import serializers
from .utils import  hash_trip_id, decode_hashed_trip_id, generate_and_store_hashed_trip_id, trip_id_mapping
from django.utils import timezone
from datetime import datetime
import uuid

@unauthenticated_user
def register_user(request):
    print("loading")
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='User')
            user.groups.add(group)

            # Log in the user after successful registration
            login(request, user)

            messages.success(request, f'Welcome, {request.user.first_name}! Your account has been successfully created.')
            return redirect('app:dashboard')
        else:
            # Print form errors to help identify the issue
            print(form.errors)

    context = {'form': form}
    return render(request, '../templates/regitser.html', context)

@unauthenticated_user
def login_register(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Determine user type and redirect accordingly
            if user.groups.filter(name='User').exists():
                return redirect('app:dashboard')  # Redirect to user dashboard
            elif user.groups.filter(name='Bus Operator').exists():
                return redirect('reservation_system:bus_operator_dashboard')  # Redirect to bus operator dashboard
            else:
                # Handle other user types or invalid group membership
                messages.error(request, 'Invalid user type or group membership.')
                return render(request, '../templates/login.html', {'form': form})  # Render login page with error message

        else:
            messages.info(request, 'Username or Password is incorrect')

    return render(request, '../templates/login.html', {'form': form})

@login_required(login_url='app:login')
def logoutUser(request):
      logout(request)
      return redirect('app:login')

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def dashboard(request):

    form_errors = request.session.pop('form_errors', None)

    user = request.user

    # Create the form with initial data if available
    form = SearchForm(initial=request.POST)

    # Your existing logic to determine the superuser
    superuser = User.objects.filter(is_superuser=True).first()

    # Check if 'passenger_details' key exists in the session
    if 'passenger_details' in request.session:
        # Delete the passenger details from the session after viewing
        del request.session['passenger_details']

    # Your other dashboard logic here
    context = {'user': user,'form': form, 'form_errors_for_travel': form_errors, 'superuser_id': superuser.id if superuser else None}
    return render(request, '../templates/dashboard.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def popular_places(request):
    context = {}
    return render(request, '../templates/popular_places.html', context)



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            current_location = form.cleaned_data['current_location']
            destination = form.cleaned_data['destination']
            date = form.cleaned_data['date']

            results = TripSchedule.objects.filter(
                origin__icontains=current_location,
                destination__icontains=destination,
                departure_date=date,
            ).select_related('bus_operator')

            serialized_results = serializers.serialize('json', results)

            request.session['results'] = serialized_results
            return redirect('app:search')  # Redirect to 'app:search' when form is valid
        else:
            # Store form errors in session
            request.session['form_errors'] = form.errors
            return redirect('app:dashboard')
    else:
        form = SearchForm()

    sort_by = request.GET.get('sort_by')
    serialized_results = request.session.get('results')

    if serialized_results:
        deserialized_results = serializers.deserialize('json', serialized_results)
        results = [trip.object for trip in deserialized_results]

        if sort_by:
            if sort_by == 'price_high_to_low':
                results.sort(key=lambda x: x.price, reverse=True)
            elif sort_by == 'price_low_to_high':
                results.sort(key=lambda x: x.price)
            elif sort_by == 'time_earliest_to_latest':
                results.sort(key=lambda x: x.departure_time)
            elif sort_by == 'time_latest_to_earliest':
                results.sort(key=lambda x: x.departure_time, reverse=True)
    else:
        results = None

    context = {'form': form, 'results': results}
    return render(request, 'search_results.html', context)



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def bookmarked_trips(request):
  
    bookmarked_trips = TripSchedule.objects.filter(bookmarked=True)
    
    
    #Display bookmarked trips from today and the days to come to prevent past trips from showing
    current_date = timezone.now().date()

    # If the date is valid (from today and onwards)
    any_valid_trips = any(trip.departure_date >= datetime.now().date() for trip in bookmarked_trips)

    print(current_date)
    context = {'bookmarked_trips':bookmarked_trips, 'current_date':current_date, 'any_valid_trips':any_valid_trips }
    return render(request, '../templates/bookmarked_trips.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
@require_POST
def update_bookmark_status(request):
    trip_id = request.POST.get('trip_id')
    bookmarked = request.POST.get('bookmarked') == 'true'
    
    try:
        trip = TripSchedule.objects.get(id=trip_id)
        trip.bookmarked = bookmarked
        trip.save()
        return JsonResponse({'success': True})
    except Trip.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trip not found'})





@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def select_tickets(request, trip_id):  # Adjust parameter name to trip_id
    # Query the TripSchedule model using the UUID
    trip = get_object_or_404(TripSchedule, id=trip_id)

    if request.method == 'POST':
        form = SelectTicketsForm(request.POST)
        if form.is_valid():
            # Save the selected number of tickets in the session or form data
            selected_number_of_tickets = form.cleaned_data['number_of_tickets']
            request.session['selected_number_of_tickets'] = selected_number_of_tickets  # Store in session
            return redirect('app:enter_passenger_details', trip_id=trip_id)  # Use trip_id
    else:
        form = SelectTicketsForm()

    context = {'trip': trip, 'form': form}
    return render(request, 'select_tickets.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def enter_passenger_details(request, trip_id):
    trip = get_object_or_404(TripSchedule, id=trip_id)
    selected_number_of_tickets = request.session.get('selected_number_of_tickets', 1)
    BuyerDetailsFormSet = inlineformset_factory(User, BuyerDetails, form=BuyerDetailsForm, fields=('name', 'phonenumber'), extra=selected_number_of_tickets, can_delete=True)
    # Retrieve passenger details from the session
    passenger_details_session = request.session.get('passenger_details', [])

    if request.method == 'POST':
        formset = BuyerDetailsFormSet(request.POST, prefix='passenger')
        if formset.is_valid():
            instances = formset.save(commit=False)

            # Add only unique passenger details to the session
            passenger_details_session = request.session.get('passenger_details', [])
            for instance in instances:
                new_passenger = {
                    'name': instance.name,
                    'phonenumber': instance.phonenumber,
                }

                # Check for duplicates before appending
                if new_passenger not in passenger_details_session:
                    passenger_details_session.append(new_passenger)

            request.session['passenger_details'] = passenger_details_session

            return redirect('app:ticket_confirmation', trip_id=trip_id)

        else:
            # Handle formset errors here, e.g., pass them to the context for rendering
            context['formset_errors'] = formset.errors

    else:
        formset = BuyerDetailsFormSet(prefix='passenger')

      # Check if 'passenger_details' key exists in the session
    if 'passenger_details' in request.session:
        # Delete the passenger details from the session after viewing
        del request.session['passenger_details']

    context = {'trip': trip, 'formset': formset}
    return render(request, 'enter_passenger_details.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def ticket_confirmation(request, trip_id):
    trip = get_object_or_404(TripSchedule, id=trip_id)
    passenger_details_session = request.session.get('passenger_details', [])
    total_price = trip.price * len(passenger_details_session)

    if request.method == 'POST':
        # Get phone number from request.POST
        phone_number = request.POST.get('modal_phone_number')

        # Check if phone number exists
        if phone_number:
            reference = generate_ticket_number()

            # Payment processing
            payment_success, payment_message = process_payment(phone_number, total_price, reference)

            if payment_success:
                create_tickets(request, trip, passenger_details_session, reference)
                send_confirmation_email(request, trip, passenger_details_session)
                
                # Clear session
                del request.session['passenger_details']
                
                messages.success(request, "Ticket successfully booked! Check your email for confirmation.")
                return redirect('app:ticket_success', trip_id=trip_id)
            else:
                messages.error(request, payment_message)
        else:
            messages.error(request, "Invalid phone number. Please enter a valid phone number.")
    
    # If not a POST request or if the phone number is empty, render the form again
    form = None  # No form needed in this case since we're not using Django forms
    context = {'trip': trip, 'passenger_details_session': passenger_details_session, 'total_price': total_price, 'form': form}
    return render(request, 'ticket_confirmation.html', context)


def generate_ticket_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def process_payment(phone_number, total_price, reference):
    try:
        if phone_number.startswith('097'):
            # Airtel Money integration
            pay_response = AirtelPay.pay(phone_number, str(total_price), "ZMW", "ZM", reference)
            print('Airtel Money Response:', pay_response)
            # Assuming AirtelPay.verify_transaction() returns True on successful payment
            verify = AirtelPay.verify_transaction(reference)
            if verify and verify.get("jsondata") and verify["jsondata"].get("data") and verify["jsondata"]["data"].get("transaction"):
                trans = verify["jsondata"]["data"]["transaction"]["status"]
                if trans == "TS":
                    return True, "Payment successful"
                else:
                    return False, "Airtel Money payment failed"
            else:
                return False, "Error occurred while verifying Airtel Money transaction"
        elif phone_number.startswith('096'):
            # MTN Money integration
            callPay = PayClass.momopay(str(total_price), "EUR", 'dp234', phone_number, "Ticket Payment")
            print('MTN Money Response:', callPay)
            # Assuming PayClass.verifymomo() returns True on successful payment
            verify = PayClass.verifymomo(callPay["ref"])
            if verify["status"] == "SUCCESSFUL":
                return True, "Payment successful"
            else:
                return False, "MTN Money payment failed"
        else:
            raise ValueError("Unsupported phone number format")
    except Exception as e:
        return False, str(e)

    
def create_tickets(request, trip, passenger_details_session, reference):
    tickets = []
    for passenger in passenger_details_session:
        ticket = Ticket.objects.create(
            buyer=request.user,
            trip=trip,
            passenger_name=passenger['name'],
            passenger_phonenumber=passenger['phonenumber'],
            ticket_no=reference,
            confirmed=True,
            active=True
        )
        ticket.save_qr_code(reference)
        tickets.append({
            'id': ticket.id,
            'passenger_name': ticket.passenger_name,
            'passenger_phonenumber': ticket.passenger_phonenumber,
            'origin': ticket.trip.origin,
            'destination': ticket.trip.destination,
            'departure_date': ticket.trip.departure_date,
            'departure_time': ticket.trip.departure_time,
            'bus_operator': ticket.trip.bus_operator.username,
        })

def send_confirmation_email(request, trip, passenger_details_session):
    subject = 'Ticket Confirmation'
    html_message = render_to_string('ticket_confirmation_email.html', {'tickets': tickets})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [request.user.email], html_message=html_message)


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def ticket_success(request, trip_id):
    user = request.user
    trip = get_object_or_404(TripSchedule, id=trip_id)
    
    # Retrieve the tickets for the specified trip and user
    tickets = Ticket.objects.filter(buyer=user, trip=trip)
    
    # Retrieve ticket numbers for each ticket
    ticket_numbers = [ticket.ticket_no for ticket in tickets]
    
    # Combine tickets and ticket_numbers into a single iterable
    ticket_data = zip(tickets, ticket_numbers)
    
    # Calculate the total price by multiplying the price of the trip by the number of tickets
    total_price = tickets.count() * trip.price
    
    # Pass the combined ticket data, trip, trip_id, and total price to the template context
    context = {'ticket_data': ticket_data, 'trip': trip, 'trip_id': trip_id, 'total_price': total_price}
    return render(request, 'ticket_success.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def cancel_confirmation(request):
    # Retrieve passenger details from the session
    passenger_details_session = request.session.get('passenger_details', [])

    # Check if 'passenger_details' key exists in the session
    if 'passenger_details' in request.session:
        # Delete the passenger details from the session after viewing
        del request.session['passenger_details']

    context = {}
    return render(request, 'dashboard.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def tickets(request):
    user = request.user
    ticket = Ticket.objects.filter(buyer=user, active=True)
    context = {'tickets': ticket}
    return render(request, 'tickets.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def previous_tickets(request):
    user = request.user
    ticket = Ticket.objects.filter(buyer=user, active=False)
    context = {'tickets': ticket}
    return render(request, 'ticket_history.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def update_ticket_active_status(request, ticket_id):
    user = request.user
    ticket = get_object_or_404(Ticket, id=ticket_id, buyer=user, active=True)
    ticket.active = False
    ticket.save()
    return redirect('app:arrived_safely')



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def user_account_details(request):
    context = {}
    return render(request, 'account_details.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def change_name(request):
    user = request.user
    form = ChangeNameForm(instance=user)

    if request.method == 'POST':
        form = ChangeNameForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'change_name.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def change_profilepic(request):
    user = request.user
    form = ChangeProfilePic(instance=user)

    if request.method == 'POST':
        form = ChangeProfilePic(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'change_profilepic.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def about_info(request):
    context = {}
    return render(request, 'about_info.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def update_ticket_active_status(request, ticket_id):
    print("Executed")
    if request.GET.get('button_clicked') == 'true':
        print("arrived.html")
        return render(request, 'arrived.html')
    else:
        print("Redirected")
        return HttpResponseRedirect(reverse('app:dashboard'))


@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def submit_suggestion(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suggestion submitted successfully!')
            return redirect('app:dashboard')  # Redirect to your desired page after success
        else:
            messages.error(request, form.errors)
    else:
        form = SuggestionForm()
    print('Error', form.errors)
    return render(request, 'arrived.html', {'form': form})






#  =====    COURIER VIEWS   =====



@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def courier_search(request):
    if request.method == 'POST':
        form = CourierSearchForm(request.POST)
        if form.is_valid():
            current_location = form.cleaned_data['current_location']
            destination = form.cleaned_data['destination']
            # Do something with the valid form data
            return redirect('enter_package_details')  # Redirect to the package details page if the form is valid
    else:
        form = CourierSearchForm()

    # If the form is not valid or it's a GET request, render the dashboard template with the form
    context = {'form': form}
    return render(request, 'dashboard.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def enter_package_details(request):
    form = PackageDetailsForm()

    if request.method == 'POST':
        form = PackageDetailsForm(request.POST)
        if form.is_valid():

            current_location = request.POST.get('current_location')
            destination = request.POST.get('destination')
            
            # Associate the sender with the current user
            package_details = form.save(commit=False)
            package_details.sender = request.user

            # Assign values to current_location and destination fields
            package_details.current_location = current_location
            package_details.destination = destination

            package_details.save()
            
            # Send email notification
            subject = 'New Package Details Submitted'
            message = (
                f"A new package details form has been submitted.\n\n"
                f"Sender ID: {request.user.id}\n"
                f"Sender Username: {request.user.username}\n"
                f"Sender Name: {request.user.first_name}\n\n"
                f"Current Location: {current_location}\n"
                f"Destination: {destination}\n\n"
                f"Package Details:\n"
                f"Item Name: {package_details.item_name}\n"
                f"Length: {package_details.length}\n"
                f"Width: {package_details.width}\n"
                f"Height: {package_details.height}\n"
                f"Weight: {package_details.weight}\n"
                f"Item Quantity: {package_details.item_quantity}\n"
                f"Fragile_Item: {package_details.fragile_item}\n"
                f"Item Category: {package_details.item_category}\n"
                f"Item_Description : {package_details.item_description }\n"
                # Include other form fields as needed
            )
            sender_email = settings.EMAIL_HOST_USER  # Your sender email address
            recipient_email = 'mutalemwango04@gmail.com'  # Your recipient email address
            send_mail(subject, message, sender_email, [recipient_email])

            messages.success(request, "Package information submitted successfully, Amount details for different courier companies will be share with you through the apps messaging system. Thank You.")
            return redirect('app:dashboard')
        else:
            print(form.errors)  

    context = {'form': form}
    return render(request, 'enter_package_details.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def superuser_messages(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to access this page.")

    form = MessageForm()
    recipients = None

    if request.method == 'GET' and 'search' in request.GET:
        search_query = request.GET.get('search')
        recipients = User.objects.filter(Q(username__icontains=search_query) | Q(id=search_query))

    if 'recipient_id' in request.GET:
        recipient_id = request.GET.get('recipient_id')
        form.fields['recipient'].initial = recipient_id

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.body = escape(request.POST.get('body')).replace('\n', '<br>')
            recipient_id = request.POST.get('recipient')
            message.recipient = User.objects.get(pk=recipient_id)
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('app:superuser_messages')

    return render(request, 'superuser_messages.html', {'form': form, 'recipients': recipients})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def inbox_list(request):
    # Retrieve distinct senders of messages sent to the logged-in user
    senders = User.objects.filter(sent_messages__recipient=request.user).distinct()

    return render(request, 'inbox_list.html', {'senders': senders})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def conversation(request, sender_id):
    sender = User.objects.get(id=sender_id)
    
    # Retrieve messages sent by the sender to the current user and vice versa
    received_messages = Message.objects.filter(recipient=request.user, sender=sender).order_by('timestamp')
    sent_messages = Message.objects.filter(sender=request.user, recipient=sender).order_by('timestamp')

    # Combine received and sent messages
    messages = received_messages | sent_messages

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            # Properly handle line breaks in the message content
            message.body = escape(request.POST.get('body')).replace('\n', '<br>')
            message.sender = request.user
            message.recipient = sender
            message.save()
            # Mark the message as unread
            message.is_read = False
            message.save()
            return redirect('app:conversation', sender_id=sender_id)
    else:
        form = MessageForm()

    context = {'messages': messages, 'sender': sender, 'form': form}
    return render(request, 'conversation.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        # Update the message content
        message.body = request.POST.get('body', '')
        message.save()
        messages.success(request, 'Message edited successfully.')
        return redirect('app:conversation', sender_id=message.sender.id)
    return render(request, 'edit_message.html', {'message': message})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    conversation_id = message.sender.id  # Assuming we redirect to the sender's conversation
    message.delete()
    # Redirect back to the conversation page where the message was deleted from
    return redirect('app:conversation', sender_id=conversation_id)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def check_new_messages(request):
    if request.user.is_authenticated:
        has_new_messages = Message.objects.filter(recipient=request.user, is_read=False).exists()
       # print('result:', has_new_messages)  # Print the result
        return JsonResponse({'has_new_messages': has_new_messages})
    return JsonResponse({'has_new_messages': False})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def mark_messages_as_read(request):
    if request.user.is_authenticated:
        sender_id = request.POST.get('sender_id')
        sender = get_object_or_404(User, id=sender_id)
        Message.objects.filter(recipient=request.user, sender=sender, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def package_payment(request):
    if request.method == 'POST':
        form = PackagePaymentForm(request.POST)
        if form.is_valid():
            package = form.save(commit=False)
            package.initiator = request.user
            package.is_active = True
            package.save()

            # Generate and save QR code
            package.save_qr_code(package.id)  # Assuming package.id is unique

            # Retrieve current location and destination from localStorage
            current_location = request.POST.get('current_location')
            destination = request.POST.get('destination')

            # Send email notification
            subject = 'New Package Payment'
            message = (
                f"A new package details form has been submitted.\n\n"
                f"Sender ID: {request.user.id}\n"
                f"Sender Username: {request.user.username}\n"
                f"Sender Name: {request.user.first_name}\n\n"
                f"Package Details:\n"
                f"Package ID: {package.id}\n"  # Use package.id as the unique identifier
                f"Courier: {package.courier}\n"
                f"Sender Name: {package.sender_name}\n"
                f"Sender Number: {package.sender_number}\n"
                f"Receiver Name: {package.receiver_name}\n"
                f"Receiver Number: {package.receiver_number}\n"
                f"Amount: {package.amount}\n"
                f"Current Location: {current_location}\n"  # Include current location
                f"Destination: {destination}\n"  # Include destination
            )
            sender_email = settings.EMAIL_HOST_USER  # Your sender email address
            recipient_email = 'mutalemwango04@gmail.com'  # Your recipient email address
            send_mail(subject, message, sender_email, [recipient_email])

            messages.success(request, 'Congratulations')
            return redirect('app:courier-receipts')  # Redirect to a success page
    else:
        form = PackagePaymentForm()

    context = {'form': form}
    return render(request, 'package_payment.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def courier_receipts(request):
    user = request.user
    courier_receipts = PackagePayment.objects.filter(initiator=user, is_active=True)

    # Retrieve current location and destination from localStorage
    current_location = request.POST.get('current_location', '')  # Change this based on how you stored it
    destination = request.POST.get('destination', '')  # Change this based on how you stored it

    context = {
        'courier_receipts': courier_receipts,
        'current_location': current_location,
        'destination': destination,
    }
    return render(request, 'courier_receipts.html', context)

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def toggle_active(request, receipt_id):
    receipt = PackagePayment.objects.get(id=receipt_id)
    receipt.is_active = not receipt.is_active
    receipt.save()
    print('success')
    return redirect('app:courier-receipts')  # Redirect back to the courier receipts page

@login_required(login_url='app:login')
@allowed_users(allowed_roles=['User'])
def fulfilled_receipts(request):
        user= request.user
        courier_receipts = PackagePayment.objects.filter(initiator=user, is_active=False)
        context = { 'courier_receipts':courier_receipts}
        return render(request, 'fulfilled_receipts.html', context)

def customer_service_inbox(request):
    # Retrieve messages where the current user is the recipient
    received_messages = CustomerService.objects.filter(receiver=request.user).order_by('-timestamp')
    
    # Group messages by sender to get a list of unique senders
    senders = {}
    for message in received_messages:
        senders[message.sender] = senders.get(message.sender, 0) + 1
    
    context = {'senders': senders}
    return render(request, '../templates/messages/customer_service_inbox.html', context)
"""
#Customer "Service"
def customer_service_message(request, sender_id):
    user = request.user
    superusers = User.objects.filter(is_superuser=True)
    sender = get_object_or_404(User, id=sender_id)

    form = CustomerServiceMessageForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        content = form.cleaned_data['content']
        
        # Determine the recipient based on the sender's role
        if user.is_superuser:
            recipient = sender
        else:
            recipient = superusers.first()
        
        # Create the message
        message = CustomerService.objects.create(sender=user, receiver=recipient, content=content)
        
        return redirect('app:customer_service_message', sender_id=sender_id)
    
    # Retrieve messages between the current user and the selected sender
    superuser = User.objects.filter(is_superuser=True).first()

    messages = CustomerService.objects.filter(
        (Q(sender=user) & Q(receiver=sender)) | (Q(sender=sender) & Q(receiver=user))
    )
    
    context = {'user': user, 'messages': messages, 'superusers': superusers, 'form': form, 'sender': sender}
    return render(request, '../templates/messages/customer_service_messages.html', context)
"""
def submit_message(request, sender_id):
    user = request.user
    sender = get_object_or_404(User, id=sender_id)
    
    form = CustomerServiceMessageForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        content = form.cleaned_data['content']
        
        # Determine the recipient based on the sender's role
        if user.is_superuser:
            recipient = sender
        else:
            recipient = User.objects.filter(is_superuser=True).first()
        
        # Create the message
        message = CustomerService.objects.create(sender=user, receiver=recipient, content=content)

        # Get the timestamp of when the message was created
        timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Assuming you have a message object containing the new message data
        new_message = {
            'content': message.content,
            'sender': message.sender.username,
            'timestamp': timestamp,  # Use the formatted timestamp
        }

        return JsonResponse(new_message)
    else:
        return JsonResponse({'error': 'Invalid form submission'})  # Return error response if form is invalid


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/reset_password.html'
    subject_template_name = 'registration/password-reset-subject.txt'
    email_template_name = 'registration/password_reset_email.html'
   


