from django import forms
from .models import Worker, WORKER_CATEGORIES, GENDER_CHOICES, EXPERIENCE_LEVEL_CHOICES

class WorkerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            'name', 'age', 'gender', 'category', 'contact_number',
            'email', 'city_name', 'skill_type', 'experience_level',
            'years_of_experience', 'profile_image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age', 'min': 18, 'required': 'required'}),
            'gender': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Phone Number', 'required': 'required', 'pattern': r'[0-9]{10}'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': 'required'}),
            'city_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'required': 'required'}),
            'skill_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill Type (e.g. Masonry, Plumbing)', 'required': 'required'}),
            'experience_level': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience', 'min': 0, 'required': 'required'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Worker.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered as a worker.")
        return email
