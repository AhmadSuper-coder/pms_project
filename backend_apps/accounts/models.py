from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class PMSUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, full_name=None, sub_id=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, sub_id=sub_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name=None, sub_id=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, sub_id, password, **extra_fields)

class PMSUser(AbstractUser):
    username = None  # remove username
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    sub_id = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = PMSUserManager()

    def __str__(self):
        return self.email
