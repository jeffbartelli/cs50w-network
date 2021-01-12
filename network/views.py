from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from .models import User, Post, Follower, Like


def index(request):
    return render(request, "network/index.html", {
        "allPosts": Post.objects.order_by('-created_date')
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def new_post(request):
    if request.method == "POST":
        post = Post()
        post.owner = request.user.username
        post.content = request.POST.get('new-post')
        post.created_date = datetime.now()
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/index.html")

def profile(request, username):
    profile = User.objects.filter(username = username)
    followerCount = Follower.objects.filter(userId = username).count()
    iFollow = Follower.objects.filter(followedId = username).count()
    myPosts = Post.objects.filter(owner = username).order_by('-created_date')

    return render(request, "network/profile.html", {
        "profile": profile,
        "followerCount": followerCount,
        "iFollow": iFollow,
        "allPosts": myPosts
    })

def following(request):
    return render(request, "network/following.html")

def likes(request, postid):
    # like = Like()
    # user = like.userId = request.user.username
    # post = like.postId = postid
    # like.save()
    # totalikes = Like.objects.filter(postId = postid).count()
    pass