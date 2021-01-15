from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    owner = models.CharField(max_length=50)
    content = models.CharField(max_length=300)
    created_date = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField('User', default=None, blank=True, related_name='likes')

class Follower(models.Model):
    star = models.CharField(max_length=50)
    followers = models.ManyToManyField('User', default=None, blank=True, related_name='followers')

class Like(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)