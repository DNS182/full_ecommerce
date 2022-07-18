from django import forms
from .models import Product, address

class AddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class Addaddress(forms.ModelForm): #its not used but can be used as form for address capturing
    class Meta:
        model = address
        exclude = ('user',)
        fields = '__all__'