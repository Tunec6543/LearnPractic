from django import forms

from .models import AdoptionApplication, WalkingBooking


class AdoptionApplicationForm(forms.ModelForm):
  class Meta:
    model = AdoptionApplication
    fields = ['housing_conditions', 'experience']
    widgets = {
        'housing_conditions': forms.Textarea(attrs={'rows': 4}),
        'experience': forms.Textarea(attrs={'rows': 4}),
    }


class WalkingBookingForm(forms.ModelForm):
  class Meta:
    model = WalkingBooking
    fields = ['date_time']
    widgets = {'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})}
