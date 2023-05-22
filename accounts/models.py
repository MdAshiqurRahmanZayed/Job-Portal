import email
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 

# Create your models here.
class MyAccountManager(BaseUserManager):
     def create_user(self,username,email,password=None):
          if not email:
               raise ValueError('User must have an email address')

          if not username:
               raise ValueError('User must have an username')
          
          user = self.model(
               email          = self.normalize_email(email),
               username       = username,
          )
          user.is_active     = True
          user.set_password(password)
          user.save(using=self._db)
          return user
     def create_superuser(self,username,email,password):
          user = self.create_user(
               email      = self.normalize_email(email),
               username   = username,
               password   = password,
          )
          user.is_admin      = True
          user.is_active     = True
          user.is_staff      = True
          user.is_superadmin = True
          user.save(using=self._db)
          return user
      
      




class Account(AbstractBaseUser):

    username      = models.CharField(max_length=50, unique=True)
    email         = models.EmailField(max_length=100, unique=True)

    #required
    date_joined   = models.DateTimeField(auto_now_add=True)
    last_login    = models.DateTimeField(auto_now_add=True)
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    

    #group
    
    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS= ['username']
    
    objects = MyAccountManager()
    
    def __str__(self):
        return self.email
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def has_perm(self,perm,obj=None):
         return self.is_admin
    
    def has_module_perms(self,add_label):
         return True
   
   
   
# User profile
JOB_TYPE = (
    ('M', "Male"),
    ('F', "Female"),
)
MARITAL_STATUS= (
     ('Married', "Married"),
    ('Unmarried', "Unmarried"),
    ('Devorced', "Devorced"),
)


ROLE = (
    ('employer', "Employer"),
    ('jobseeker', "Job Seeker"),
)


class UserProfile(models.Model):
    user            = models.OneToOneField(Account, on_delete=models.CASCADE)
    first_name      = models.CharField(max_length=50,blank=False,null=False)
    last_name       = models.CharField(max_length=50,blank=False,null=False)
    father_name     = models.CharField(max_length=50,blank=False,null=False)
    mother_name     = models.CharField(max_length=50,blank=False,null=False)
    religion        = models.CharField(max_length=50,blank=False,null=False)
    nationality     = models.CharField(max_length=50,blank=False,null=False)
    occupation      = models.CharField(max_length=50,blank=False,null=False)
    nid_no          = models.IntegerField(blank=False,null=False)
    nid_image       = models.ImageField(blank=False,null=False, upload_to='images/nid')
    birth_date      = models.DateField( auto_now=False, auto_now_add=False)
    website         = models.CharField(max_length=70,blank=True,null=True)
    linkedin        = models.CharField(blank=True,null=True, max_length=50)
    about           = models.TextField()
    phone_number    = models.CharField(max_length=50,blank=False,null=False)
    profile_picture = models.ImageField(blank=True,null=True, upload_to='images/profile',default='images/man.png')
    present_address  = models.CharField(blank=False,null=False, max_length=100)
    permanent_address  = models.CharField(blank=False,null=False, max_length=100)
    gender = models.CharField(blank=False,null=False, choices=JOB_TYPE, max_length=1)
    marital_status = models.CharField(blank=False,null=False, max_length=20 ,choices=MARITAL_STATUS)
    
    role = models.CharField(choices=ROLE,  max_length=10)

    
    
    def get_full_name(self):
        return self.first_name+ ' ' + self.last_name
    
     
    def __str__(self):
        return self.user.username


#Education    
GROUP = (
    ('science','Science'),
    ('commerce','Commerce'),
    ('arts','Arts'),
)
BOARD = (
    ('dhaka','Dhaka'),
    ('rajshahi','Rajshahi'),
    ('comilla','Comilla'),
    ('jessore','Jessore'),
    ('chittagong','Chittagong'),
    ('barisal','Barisal'),
    ('sylhet','Sylhet'),
    ('dinajpur','Dinajpur'),
    ('madrasah','Madrasah'),
    ('technical','Technical'),
)


class Education(models.Model):
    # user = models.ForeignKey(UserProfile, related_name='UserEducation', on_delete=models.CASCADE) 
    user = models.OneToOneField(UserProfile, related_name='UserEducation', on_delete=models.CASCADE) 
    
    #ssc/Equivalent
    ssc_group = models.CharField(choices=GROUP, max_length=10,null=True,blank=True)
    ssc_year  = models.DateField( auto_now=False, auto_now_add=False,null=True,blank=True)
    ssc_board = models.CharField(choices=BOARD, max_length=50,null=True,blank=True)
    ssc_institution = models.CharField( max_length=50,null=True,blank=True)
    ssc_cgpa = models.FloatField(null=True,blank=True)
    ssc_certificate = models.FileField( upload_to=f'applicant/certificate/', max_length=100,null=True,blank=True)
    
    #hsc/Equivalent
    hsc_group = models.CharField(choices=GROUP, max_length=10,null=True,blank=True)
    hsc_year  = models.DateField( auto_now=False, auto_now_add=False,null=True,blank=True)
    hsc_board = models.CharField(choices=BOARD, max_length=50,null=True,blank=True)
    hsc_cgpa = models.FloatField(null=True,blank=True)
    hsc_institution = models.CharField( max_length=50,null=True,blank=True)
    hsc_certificate = models.FileField( upload_to=f'applicant/certificate/', max_length=100,null=True,blank=True)
    
    #bsc/Equivalent
    bsc_session = models.CharField( max_length=20,null=True,blank=True)
    bsc_institution = models.CharField( max_length=50,null=True,blank=True)
    bsc_graduation_year = models.DateField( auto_now=False, auto_now_add=False,null=True,blank=True)
    bsc_subject = models.CharField( max_length=50,null=True,blank=True)
    bsc_cgpa = models.FloatField(null=True,blank=True)
    bsc_certificate = models.FileField( upload_to=f'applicant/certificate/', max_length=100,null=True,blank=True)
    
    
    
    #msc/Equivalent
    msc_session = models.CharField( max_length=20,null=True,blank=True)
    msc_institution = models.CharField( max_length=50,null=True,blank=True)
    msc_graduation_year = models.DateField( auto_now=False, auto_now_add=False,null=True,blank=True)
    msc_subject = models.CharField( max_length=50,null=True,blank=True)
    msc_cgpa = models.FloatField(null=True,blank=True)
    msc_certificate = models.FileField( upload_to=f'applicant/certificate/', max_length=100,null=True,blank=True)

    
    created_at = models.DateTimeField(auto_now_add = True) 
    modified_at = models.DateTimeField(auto_now = True) 
    
 
    
    def __str__(self):
        return self.user