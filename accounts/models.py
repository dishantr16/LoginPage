from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
# Create your models here.

from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import random
import os
import requests


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_superuser = True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    CHOICES = (
        ("WOMEN_ENTREPRENEUR", "Women Entrepreneur"),
        ("INFLUENCER", "Influencer"),
        ("BUYER", "Buyer")
    )

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,10}$',
                                 message="Phone number must be entered in the format +919999999999. Up to 10 digits")
    phone = models.CharField('Phone', validators=[phone_regex], max_length=10, unique=True)
    REQUIRED_FIELDS = ['username', 'phone']

    objects = UserManager()
