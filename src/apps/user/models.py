from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set", 
        blank=True,
        )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_set", 
        blank=True,
        )

    def __str__(self):
        return "{} {} [{}]".format(self.last_name, self.first_name, self.username)


