from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Hairdresser, Service


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'username': 'Username',
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
            'password1': 'Password',
            'password2': 'Confirm password',
        }
        placeholders = {
            'username': 'Enter your username',
            'first_name': 'Enter your first name',
            'last_name': 'Enter your last name',
            'email': 'Enter your email address',
            'password1': 'Enter your password',
            'password2': 'Re-enter your password',
        }
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        for name, field in self.fields.items():
            field.label = labels.get(name, field.label)
            field.widget.attrs['placeholder'] = placeholders.get(name, '')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select'
            else:
                widget.attrs['class'] = 'form-control'


class ServiceForm(StyledModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'description', 'image_url']
        labels = {
            'name': 'Service name',
            'price': 'Price',
            'description': 'Description',
            'image_url': 'Image URL',
        }


class HairdresserForm(StyledModelForm):
    class Meta:
        model = Hairdresser
        fields = ['name', 'specialization', 'experience', 'bio', 'image_url', 'is_verified']
        labels = {
            'name': 'Hairdresser name',
            'specialization': 'Specialization',
            'experience': 'Experience',
            'bio': 'Biography',
            'image_url': 'Image URL',
            'is_verified': 'Verified',
        }


class BookingForm(StyledModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Booking
        fields = [
            'full_name',
            'phone',
            'service',
            'appointment_date',
            'appointment_time',
            'location',
            'notes',
            'payment_method',
        ]
        labels = {
            'full_name': 'Full name',
            'phone': 'Phone',
            'service': 'Service',
            'appointment_date': 'Appointment date',
            'appointment_time': 'Appointment time',
            'location': 'Location',
            'notes': 'Notes',
            'payment_method': 'Payment method',
        }


class BookingAdminForm(StyledModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Booking
        fields = [
            'full_name',
            'phone',
            'service',
            'hairdresser',
            'appointment_date',
            'appointment_time',
            'location',
            'notes',
            'payment_method',
            'payment_status',
            'status',
        ]
        labels = {
            'full_name': 'Customer name',
            'phone': 'Phone',
            'service': 'Service',
            'hairdresser': 'Hairdresser',
            'appointment_date': 'Appointment date',
            'appointment_time': 'Appointment time',
            'location': 'Location',
            'notes': 'Notes',
            'payment_method': 'Payment method',
            'payment_status': 'Payment status',
            'status': 'Order status',
        }
