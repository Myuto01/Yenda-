from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from reservation_system.models import BuyerDetails, PackageDetails, Suggestion
from django.forms import formset_factory

#User Forms
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]

# Change Name
class ChangeNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username','email']


# Change Profile Pic
class ChangeProfilePic(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']

#Login Form
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SearchForm(forms.Form):
    current_location = forms.CharField(label='From', max_length=100, error_messages={'required': 'Please provide your current location.'})
    destination = forms.CharField(label='To', max_length=100,  error_messages={'required': 'Please provide your destination.'})
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}), error_messages={'required': 'Please select a date.'})
  

class BuyerDetailsForm(forms.ModelForm):
    class Meta:
        model = BuyerDetails
        fields = ['name', 'phonenumber']

class SelectTicketsForm(forms.Form):
    number_of_tickets = forms.IntegerField(min_value=1, label='Number of Tickets')

class CourierSearchForm(forms.Form):
    current_location = forms.CharField(label='From', max_length=100)
    destination = forms.CharField(label='To', max_length=100)
    date = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))


class PackageDetailsForm(forms.ModelForm):
    class Meta:
        model = PackageDetails
        fields = [
            'item_name',
            'length', 
            'width', 
            'height', 
            'weight', 
            'item_quantity', 
            'fragile_item',
            'item_category', 
            'item_description',
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'Enter item name', 'class': 'item-name'}),
            'length': forms.NumberInput(attrs={'placeholder': 'Enter length', 'class': 'item-name-l'}),
            'width': forms.NumberInput(attrs={'placeholder': 'Enter width', 'class': 'item-name-w'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Enter height', 'class': 'item-name-h'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Enter weight', 'class': 'item-name'}),
            'item_quantity': forms.NumberInput(attrs={'placeholder': 'Enter item quantity', 'class': 'item-name'}),
            'item_category': forms.TextInput(attrs={'placeholder': 'Enter item category', 'class': 'item-name'}),
            'item_description': forms.Textarea(attrs={'placeholder': 'Enter item description', 'class': 'description-input', 'rows': 4, 'cols': 50, 'style': 'resize: none;', 'autolink': 'true'}),
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['description']








"""
class SeatSelectionForm(forms.Form):
    MAX_ROWS = 10
    MAX_COLUMNS = 6

    seat_choices = [(f"{row}-{column}", f"{row}-{column}") for row in range(1, MAX_ROWS + 1) for column in range(1, 6 + 1)]

    selected_seats = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=seat_choices)
"""