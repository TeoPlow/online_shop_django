from django.contrib.auth.models import AbstractUser
from django.db import models


class Image(models.Model):
    """Модель изображения"""

    src = models.ImageField(upload_to="images/")
    alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.alt or str(self.src)


class User(AbstractUser):
    """Модель пользователя"""

    fullName = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_avatars",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
