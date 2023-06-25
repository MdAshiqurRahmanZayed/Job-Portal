from django import forms
from .models import UserProfile
from django import forms 
from .models import Account,UserProfile,Education



class RegistrationForm(forms.models.ModelForm):
     password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
     }))
     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        
     }))

     
     class Meta:
          model = Account
          fields = ['email', 'password']

     def clean(self):
          cleaned_data = super(RegistrationForm, self).clean()
          password = cleaned_data.get('password')
          confirm_password = cleaned_data.get('confirm_password')
          
          if password != confirm_password:
               raise forms.ValidationError(
                    "Password does not match!"
               )
          
               
     def __init__(self, *args, **kwargs):
          super(RegistrationForm, self).__init__(*args, **kwargs)
          self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'
               
class DateInput(forms.DateInput):
    input_type = 'date'

               
class createProfile(forms.models.ModelForm):
     class Meta:
          model = UserProfile
          fields = ['first_name', 'last_name','father_name','mother_name','religion','nationality','occupation','nid_no','nid_image','birth_date','website','linkedin','about','phone_number','profile_picture','present_address','permanent_address','gender','marital_status','role']

          
     birth_date = forms.DateField(widget=DateInput)
     def __init__(self, *args, **kwargs):
          super(createProfile, self).__init__(*args, **kwargs)
          for field in self.fields:
              self.fields[field].widget.attrs['class'] = 'form-control'



class updateProfile(forms.models.ModelForm):

     class Meta:
          model = UserProfile
          fields = ['first_name', 'last_name', 'father_name', 'mother_name', 'religion', 'nationality', 'occupation', 'nid_no', 'nid_image', 'birth_date', 'website',
                    'linkedin', 'about', 'phone_number', 'profile_picture', 'background_profile_picture', 'present_address', 'permanent_address', 'gender', 'marital_status']
          
     
     def __init__(self, *args, **kwargs):
          super(updateProfile, self).__init__(*args, **kwargs)

          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'

       
class dateInput(forms.DateInput):
     input_type = "date"

       

class educationForm(forms.models.ModelForm):
     ssc_year = forms.DateField(widget=dateInput ,required=False)
     hsc_year = forms.DateField(widget=dateInput,required=False)
     bsc_graduation_year = forms.DateField(widget=dateInput,required=False)
     msc_graduation_year = forms.DateField(widget=dateInput,required=False)

     class Meta:
          model  = Education
          fields = ['ssc_group','ssc_year','ssc_board','ssc_institution','ssc_cgpa','ssc_certificate','hsc_group','hsc_year','hsc_board','hsc_cgpa','hsc_institution','hsc_certificate','bsc_session','bsc_institution','bsc_graduation_year','bsc_subject','bsc_cgpa','bsc_certificate','msc_session','msc_institution','msc_graduation_year','msc_subject','msc_cgpa','msc_certificate']
          
     def __init__(self, *args, **kwargs):
          super(educationForm, self).__init__(*args, **kwargs)
          for field in self.fields:
               self.fields[field].widget.attrs['class'] = 'form-control'
               
               
               
                       
     