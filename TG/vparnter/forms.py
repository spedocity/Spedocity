from django import forms
from .models import PartnerInfo

class PartnerInfoForm(forms.ModelForm):
    class Meta:
        model = PartnerInfo
        fields = ['alternative_phone', 'dob', 'adhar_no', 'dl', 'dl_document', 'profile_picture', 'address']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }