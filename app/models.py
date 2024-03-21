from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

def profile_pics_upload_path(instance, filename):
    # Upload to "citizen_id/username/front" or "citizen_id/username/back"
    return f'profile_pics/{instance.username}/{filename}'

class User(AbstractUser):
    first_name = models.CharField(max_length=30, null=True, default="")
    last_name = models.CharField(max_length=30, null=True, default="")
    email = models.EmailField(null=False, default="")
    profile_pic = models.ImageField(default='default1.jpg', null=True, blank=True, upload_to=profile_pics_upload_path)
    # Provide unique related names to avoid clashes
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')
