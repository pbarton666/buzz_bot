from django import forms

'''
Display searches, allow edits
'''
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
