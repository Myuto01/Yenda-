from django.contrib.auth.models import AbstractUser
from django.db import models
from app.models import User
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class ReservationSystemUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reservationsystemuser')
    email = models.EmailField(null=False, default="")
    total_seats = models.IntegerField(default=0)
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user}'

class TripSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
    bus_operator = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    driver = models.CharField(max_length=100, default="")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField(default=timezone.now)
    departure_time = models.TimeField(default=timezone.now)
    estimated_arrival_time = models.TimeField(default=timezone.now)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    bookmarked = models.BooleanField(default=False)
    
    def __str__(self):
            return f'{self.bus_operator}'

class BuyerDetails(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(TripSchedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    phonenumber = models.CharField(max_length=15, default="")
    confirmed = models.BooleanField(default=False)  # Add this field

class Tickets(models.Model):
    buyer_name = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer_trip = models.ForeignKey(TripSchedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, null=True, blank=True)  # Track payment status (e.g., new, paid, failed)
    timestamp = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(TripSchedule, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=15, default="", null=True)
    passenger_phonenumber = models.CharField(max_length=15)
    confirmed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    ticket_no = models.CharField(max_length=100, default="")
    
    #QR Code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save_qr_code(self, ticket_number):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_number)
        qr.make(fit=True)

        qr_code_io = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_code_io, format='PNG')

        self.qr_code.save(f'qr_code_{self.id}.png', ContentFile(qr_code_io.getvalue()), save=False)
        super().save()

    def __str__(self):
        return f"Ticket ID: {self.ticket_id}, Passenger: {self.passenger_name}, Trip: {self.trip}"



# ===== COURIER SERVICES =====
class PackageDetails(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100, default="")
    length =  models.DecimalField(max_digits=8, decimal_places=2)
    width =   models.DecimalField(max_digits=8, decimal_places=2)
    height = models.DecimalField(max_digits=8, decimal_places=2)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    item_quantity = models.IntegerField(default=1)
    fragile_item = models.BooleanField(default=False, null=True, blank=True)
    item_category = models.CharField(max_length=100, default="")
    item_description = models.TextField()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=100)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - From: {self.sender.username} To: {self.recipient.username}"

class PackagePayment(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='package_payment')
    pesapal_transaction_tracking_id = models.CharField(max_length=100, default='', null=True, blank=True)
    package_id = models.IntegerField( default=0)
    courier = models.CharField(max_length=20, default="")
    sender_name = models.CharField(max_length=20, default="")
    sender_number = models.CharField(max_length=20, default="")
    receiver_name =  models.CharField(max_length=20, default="")
    receiver_number =models.CharField(max_length=20, default="")
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=20, null=True, blank=True)  # Track payment status (e.g., new, paid, failed)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    qr_code = models.ImageField(upload_to='courier receipt-qr_codes/', blank=True, null=True)

    def save_qr_code(self, package_id):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(package_id)
        qr.make(fit=True)

        qr_code_io = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_code_io, format='PNG')

        self.qr_code.save(f'qr_code_{self.id}.png', ContentFile(qr_code_io.getvalue()), save=False)
        super().save()


class CustomerService(models.Model):
    sender = models.ForeignKey(User, related_name='customer_service_sent_messages', on_delete=models.CASCADE, default=None)
    receiver = models.ForeignKey(User, related_name='customer_service_received_messages', on_delete=models.CASCADE, default=None)
    content = models.TextField(default='')
    read = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content}"


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  # Optional user association
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatic timestamp
  
    def __str__(self):
        return f"{self.description} - {self.user}"




































    

    """
    # New fields to store the number of rows and columns
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)

# models.py
class Seat(models.Model):
    bus_operator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    trip_schedule = models.ForeignKey(TripSchedule, on_delete=models.CASCADE, null=True)
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_seats', null=True)
    seat_number = models.CharField(max_length=10)
    column = models.IntegerField(default=0)  # Add this line for the column field
    row = models.IntegerField(default=0) 
    is_available = models.BooleanField(default=True)

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    seats = models.ManyToManyField(Seat)
    """