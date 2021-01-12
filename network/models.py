from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    owner = models.CharField(max_length=64)
    content = models.CharField(max_length=300)
    created_date = models.DateTimeField(auto_now_add=True)

class Follower(models.Model):
    userId = models.CharField(max_length=64)
    followedId = models.CharField(max_length=64)

class Like(models.Model):
    userId = models.CharField(max_length=64)
    postId = models.IntegerField()