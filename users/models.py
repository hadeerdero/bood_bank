from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

class User(AbstractUser):
    USER_ROLES = (
        ('donor', 'Donor'),
        ('hospital', 'Hospital'),
        ('bloodBank', 'bloodBank'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",  # Changed from 'user_set'
        related_query_name="user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",  # Changed from 'user_set'
        related_query_name="user",
    )

    def tokens(self):
        token = RefreshToken.for_user(self)
        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }