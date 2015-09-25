#form handling routines here
from django.forms import  ModelForm
import models

class SearchForm(ModelForm):
    class Meta:
        model = models.Search

class ContactForm():
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)
