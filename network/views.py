import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

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
    profile = User.objects.get(username = username)
    # followerCount = Follower.objects.filter(userId = username).count()
    # iFollow = Follower.objects.filter(followedId = username).count()
    myPosts = Post.objects.filter(owner = username).order_by('-created_date')

    user = request.user
    follows = Follower.objects.get_or_create(star=profile)[0]
    if user in follows.followers.all():
        followText = "Unfollow"
    else:
        followText = "Follow"

    return render(request, "network/profile.html", {
        "profile": profile,
        # "followerCount": followerCount,
        # "iFollow": iFollow,
        "allPosts": myPosts,
        "state": followText
    })

def following(request):
    return render(request, "network/following.html")

@csrf_exempt
@login_required
def follow(request):
    followText = ''
    user = request.user
    # Retrieve the Data
    data = json.loads(request.body)
    target = data.get("target", "")
    follows = Follower.objects.get_or_create(star=target)[0]
    if user in follows.followers.all():
        follows.followers.remove(user)
        followText = "Follow"
    else:
        follows.followers.add(user)
        follows.save()
        followText = "Unfollow"
    
    return JsonResponse({
        "followText": followText
    }, status=201)

@csrf_exempt
@login_required
def likes(request):
    liker = ''
    user = request.user
    # Retrieve the data
    data = json.loads(request.body)
    postId = data.get("postId", "")
    likedPost = Post.objects.get(pk=postId)
    if user in likedPost.liked.all():
        likedPost.liked.remove(user)
        liked = Like.objects.get(post=likedPost, user=user)
        liked.delete()
        liker = 'Like'
    else:
        liked = Like.objects.get_or_create(post=likedPost, user=user)
        likedPost.liked.add(user)
        likedPost.save()
        liker = 'Unlike'
    # Return the liker count and value
    return JsonResponse({
        "count": likedPost.liked.all().count(),
        "liker": liker
        }, status=201)

def edit(request):
    pass