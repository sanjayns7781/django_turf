from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class Role(models.Model):
    ROLE_CHOICES = [
    ('ADMIN', 'ADMIN'),
    ('OWNER', 'OWNER'),
    ('CUSTOMER', 'CUSTOMER'),
    ]
    name = models.CharField(max_length=50,choices=ROLE_CHOICES)
    description = models.CharField(max_length=200)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_db'

    def __str__(self):
        return f'{self.name}'



class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")

        # Assign ADMIN role automatically
        
        extra_fields['role'] = Role.objects.get(name="ADMIN")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    role = models.ForeignKey(Role,on_delete=models.CASCADE)

    objects = UserManager()

    class Meta:
        db_table = 'user_db'

    def __str__(self):
        return f"{self.username}----{self.email}-----{self.role}"

