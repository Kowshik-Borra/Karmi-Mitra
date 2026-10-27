# pyrefly: ignore [missing-import]
from django import forms
from .models import Feedback, RATING_CHOICES

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['customer_name', 'rating', 'comments']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', 'required': 'required'}),
            'rating': forms.Select(choices=RATING_CHOICES, attrs={'class': 'form-select', 'required': 'required'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your feedback or comments...'}),
        }
