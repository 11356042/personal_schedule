from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# 1. 班級表
class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="班級名稱")

    def __str__(self):
        return self.name

# 2. 用戶身分擴充表 (1 對 1 關聯 auth_user)
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', '學生'),
        ('teacher', '老師'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="真實姓名")
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="學號/教職號")
    
    school_class = models.ForeignKey(
        SchoolClass, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="班級"
    )

    def __str__(self):
        return f"{self.real_name or self.user.username} ({self.get_role_display()})"