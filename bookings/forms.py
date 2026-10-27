from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'customer_name', 'customer_age', 'customer_address',
            'customer_contact', 'customer_email', 'work_details', 'location_url'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'required': 'required'}),
            'customer_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age', 'min': 18, 'required': 'required'}),
            'customer_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Address', 'required': 'required'}),
            'customer_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Details', 'required': 'required'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': 'required'}),
            'work_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe work details...', 'required': 'required'}),
            'location_url': forms.URLInput(attrs={'class': 'form-control', 'id': 'customer_location', 'placeholder': 'Location URL (e.g. Google Maps link)'}),
        }

class OTPVerificationForm(forms.Form):
    booking_id = forms.IntegerField(widget=forms.HiddenInput())
    worker_id = forms.IntegerField(widget=forms.HiddenInput())
    otp = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg text-center', 'placeholder': 'Enter 6-digit OTP', 'required': 'required', 'autocomplete': 'off'}))
