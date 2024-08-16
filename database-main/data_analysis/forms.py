from django import forms

class DateSelectorForm(forms.Form):
    selected_date = forms.DateField(widget=forms.SelectDateWidget, label="Select Date")


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget)
    end_date = forms.DateField(widget=forms.SelectDateWidget)