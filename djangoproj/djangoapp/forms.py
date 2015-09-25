from django import forms
import models

class SearchForm(forms.ModelForm):
    class Meta:
        model = models.Search

'''
Display searches, allow edits
'''
class warningForm(forms.Form):
    message = forms.CharField()
    action = forms.CharField()
    searchid = forms.CharField()
    redirect = forms.CharField()

class displaySearchForm(forms.Form):
	title = forms.CharField()
	include = forms.CharField()
	exclude= forms.CharField(required = False)
	
class displaySubSearches(forms.Form):
	title = forms.CharField()
	include = forms.CharField()
	exclude= forms.CharField(required = False)		
class editCriteria(forms.Form):
	title = forms.CharField()
	include = forms.CharField()
	exclude= forms.CharField(required = False)	
