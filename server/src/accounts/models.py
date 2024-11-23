from django.contrib.auth.models import AbstractUser
# from django.db import models

class CustomUser(AbstractUser):
    # 추가 필드를 원한다면 아래에 작성
    # example: phone_number = models.CharField(max_length=15, blank=True, null=True)
    pass
