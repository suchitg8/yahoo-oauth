from django.db import models

# Create your models here.

class UserModel(models.Model):
    email = models.EmailField(null=True, max_length=225)
    nickname = models.CharField(max_length=225)
    imageurl = models.CharField(max_length=225)
    user_id = models.CharField(max_length=50)

