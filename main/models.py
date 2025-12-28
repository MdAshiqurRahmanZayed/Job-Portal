# from taggit.managers import TaggableManager

from ckeditor.fields import RichTextField
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from accounts.models import UserProfile


def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=5)
    return unique_slug


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, max_length=100, unique=True)
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)


JOB_TYPE = (
    ("fulltime", "Full time"),
    ("parttime", "Part time"),
    ("remote", "Remote"),
    ("internship", "Internship"),
)


class Job(models.Model):
    user = models.ForeignKey(UserProfile, related_name="User", on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    slug = models.SlugField(allow_unicode=True, max_length=200, unique=True)
    category = models.ForeignKey(
        Category, related_name="Category", on_delete=models.CASCADE
    )
    description = RichTextField()
    company_name = models.CharField(max_length=300)
    company_description = models.TextField(null=True, blank=True)
    company_email = models.EmailField(max_length=254, null=False, blank=False)
    company_image = models.ImageField(
        null=True,
        blank=True,
        upload_to="jobs/image",
        default="images/default/default.jpg",
    )
    vacancy = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=300, default="Worldwide")
    job_type = models.CharField(choices=JOB_TYPE, max_length=10)
    salary = models.CharField(max_length=30, blank=True)
    website_url = models.URLField(max_length=200)
    deadline = models.DateField()
    is_published = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    #     def save(self,*args, **kwargs):
    #          if self.slug:
    #               self.slug = slugify(self.name ,allow_unicode=True)
    #          return super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(
        UserProfile, related_name="applicantUser", on_delete=models.CASCADE
    )
    content = RichTextField()
    resume = models.FileField(upload_to="applicant/resume", max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job.title


class ConversationMessages(models.Model):
    application = models.ForeignKey(
        Application, related_name="conversationmessages", on_delete=models.CASCADE
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        UserProfile, related_name="conversationmessages", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]


NOTIFICATION_CHOICES = (
    ("message", "message"),
    ("application", "application"),
)


class Notification(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        UserProfile, related_name="notifications", on_delete=models.CASCADE
    )
    notification_type = models.CharField(choices=NOTIFICATION_CHOICES, max_length=20)
    is_seen = models.BooleanField(default=False)
    extra_id = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        UserProfile, related_name="creatednotifications", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class Review(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    description = models.CharField(max_length=400)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    show = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.user}"


# About page
class AboutPage(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    about = models.TextField()
    image = models.ImageField(
        upload_to="about/", height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.name


# Team member
class teamMember(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    about = models.TextField()
    image = models.ImageField(
        upload_to="teamMember/", height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.name
