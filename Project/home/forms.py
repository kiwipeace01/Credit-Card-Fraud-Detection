from django import forms
from django.db import models

class LoginForm(forms.Form):
    your_name = forms.CharField(max_length=100)
    your_pass = forms.CharField(max_length=100)

class SignForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    fpass = forms.CharField(max_length=100)
    re_pass = forms.CharField(max_length=100)

class CardForm(forms.Form):
    # adr = forms.CharField(max_length=100)
    aadhar = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=100) 
    nation = forms.CharField(max_length=100) 
    date = models.DateTimeField() 

class TransactionForm(forms.Form):
    date = forms.DateTimeField()
    amount = forms.CharField(max_length=100)
    cname = forms.CharField(max_length=100)
    ccnum = forms.CharField(max_length=100)
    expyear = forms.CharField(max_length=100) 
    cvv = forms.CharField(max_length=100) 

class AdminForm(forms.Form):
    email = forms.CharField(max_length=100)

    