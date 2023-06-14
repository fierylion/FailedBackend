from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from datetime import datetime
# Create your models here.
# q: I want to create a model where users can register login and add companies , and there will be subscripiton where various packages will offer various thing
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, verbose_name='username', error_messages={'unique': 'A user with that username already exists.'})
    email = models.EmailField(verbose_name='email address', unique=True, error_messages={'unique': 'A user with that email already exists.'})
    password = models.CharField(max_length=255, verbose_name='password')
    phone = models.CharField(max_length=20, verbose_name='phone')
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    package_created_at = models.DateTimeField(default=datetime(2002, 1, 1, 0, 0,0))
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
class Package(models.Model):
    type = models.CharField(max_length=255, primary_key=True)
    price = models.IntegerField()
    max_no_of_companies = models.IntegerField()
    isEmailReminders = models.BooleanField(default=False)
    def __str__(self):
        return self.type