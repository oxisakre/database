from django import forms

class DateSelectorForm(forms.Form):
    selected_date = forms.DateField(widget=forms.SelectDateWidget, label="Select Date")


class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))