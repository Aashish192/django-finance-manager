from django import forms
from .models import Transition
from django.contrib.auth.models import User

class TransitionForm(forms.ModelForm):
    class Meta:
        model = Transition
        fields = ['type', 'amount', 'description', 'date']

        widgets = {
            'type': forms.Select(attrs={
                'class': 'border rounded px-3 py-1',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'border rounded px-3 py-1',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'border rounded px-3 py-1',
                'rows': 3,
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'border rounded px-3 py-1',
            }),
        }

        
class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    class Meta:
        model = User
        fields = ['username','password']