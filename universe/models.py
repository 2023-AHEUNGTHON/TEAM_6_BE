from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager


# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        user = self.model(
            email = self.normalize_email(email), # 학교 이메일
            password = password, # 비밀번호
            **extra_fields
            )
        user.set_password(password)
        user.save(using=self._db)
        print(user)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, null=False)
    grade = models.CharField(max_length=20, null=False)
    school = models.CharField(max_length=20, null=False)
    email = models.EmailField(max_length=50, null=False, unique=True)
    major = models.CharField(max_length=20, null=False)
    project = models.CharField(max_length=20, null=False)
    student_id = models.CharField(max_length=20, null=False)
    password = models.CharField(max_length=100, null=False)
    available = models.CharField(max_length=30, null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

class Write(models.Model):
    content=models.TextField()
    category=models.CharField(max_length=20,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return f'{self.content} [{self.id}]'