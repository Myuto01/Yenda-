from django import forms
from app.models import User
from .models import ReservationSystemUser, TripSchedule, Message, PackagePayment, CustomerService
from django.contrib.auth.forms import UserCreationForm
import re

#User Forms
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        # Adding placeholders for each form field
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class TripScheduleForm(forms.ModelForm):
    class Meta:
        model = TripSchedule
        fields = ['driver', 'origin', 'destination', 'departure_date', 'departure_time', 'estimated_arrival_time', 'price']
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'estimated_arrival_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        
        } 

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Start typing..', 'rows': 4, 'cols': 50, 'style': 'resize: none;', 'autolink': 'true'}),
        }

class PackagePaymentForm(forms.ModelForm):
    package_id = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Enter Package ID', 'class': 'pkg_payment-input'}))
    amount = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Enter required amount', 'class': 'pkg_payment-input'}))
    class Meta:
        model = PackagePayment
        fields = ['initiator','package_id', 'courier', 'sender_name', 'sender_number', 'receiver_name', 'receiver_number', 'amount']
        widgets = {
            'courier': forms.TextInput(attrs={'placeholder': 'Enter Courier of Choice', 'class': 'pkg_payment-input'}), 
            'sender_name': forms.TextInput(attrs={'placeholder': 'Enter Sender`s name', 'class': 'pkg_payment-input'}), 
            'sender_number': forms.TextInput(attrs={'placeholder': 'Enter Sender`s number', 'class': 'pkg_payment-input'}), 
            'receiver_name': forms.TextInput(attrs={'placeholder': 'Enter Receiver`s name', 'class': 'pkg_payment-input'}), 
            'receiver_number': forms.TextInput(attrs={'placeholder': 'Enter Receiver`s name', 'class': 'pkg_payment-input'}), 
        }       

class CustomerServiceMessageForm(forms.ModelForm):
    content = forms.CharField(label='Message', widget=forms.Textarea)
    original_sender_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    
    class Meta:
        model =  CustomerService
        fields = [
            'original_sender_id',
            'content'
        ]


class TicketConfirmationForm(forms.Form):
    modal_phone_number = forms.CharField(max_length=20, required=True)

