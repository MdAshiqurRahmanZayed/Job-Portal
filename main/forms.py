from django import forms 
from .models import *
from taggit.models import Tag 

class dateInput(forms.DateInput):
     input_type = "date"


class jobForms(forms.models.ModelForm):
     deadline = forms.DateField(widget=dateInput)
     is_published = forms.BooleanField()
     tags = forms.ModelMultipleChoiceField(label='Tags', queryset=Tag.objects.order_by('name'),widget=forms.SelectMultiple)

     class Meta:
          model = Job
          fields = ['title', 'category', 'description', 'company_name', 'company_description', 'company_email', 'vacancy',
                    'company_image', "tags", 'location', 'job_type', 'salary', 'website_url', 'deadline', 'is_published', 'is_closed']
     
     
     def __init__(self, *args, **kwargs):
          super(jobForms, self).__init__(*args, **kwargs)
          self.fields['salary'].widget.attrs['placeholder'] = 'exp:50,000-80,000'
          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'
          # self.fields['deadline'].widget.attrs['class'] = 'col-md-6'
          self.fields['is_published'].widget.attrs['class'] = 'form-check-input'
          self.fields['is_closed'].widget.attrs['class'] = 'form-check-input'


class applicationForm(forms.models.ModelForm):
     class Meta:
          model  = Application
          fields = ['content','resume']
          
     def __init__(self, *args, **kwargs):
          super(applicationForm, self).__init__(*args, **kwargs)
          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'
               
class ConversationMessagesForm(forms.models.ModelForm):
     class Meta:
          model  = ConversationMessages
          fields = ['content']
          
     def __init__(self, *args, **kwargs):
          super(ConversationMessagesForm, self).__init__(*args, **kwargs)
          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'
               
               
