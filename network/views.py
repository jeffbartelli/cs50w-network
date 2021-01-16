import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post, Follower, Like

def index(request):
    posts = Post.objects.order_by('-created_date')
    pageNumber = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    
    try:
        postSet = paginator.page(pageNumber)
    except PageNotAnInteger:
        postSet = paginator.page(1)
    except EmptyPage:
        postSet = paginator.page(paginator.num_pages)

    
    return render(request, "network/index.html", {
        "allPosts": postSet
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
    followerCount = Follower.objects.filter(star = username).count()
    iFollow = Follower.objects.filter(follower = username).count()
    myPosts = Post.objects.filter(owner = username).order_by('-created_date')

    user = request.user
    follows = Follower.objects.filter(star=profile, follower=user)
    if not follows:
        followText = "Follow Me"
    else:
        followText = "Unfollow Me"

    page = request.GET.get('page', 1)
    paginator = Paginator(myPosts, 10)
    try:
        postSet = paginator.page(page)
    except PageNotAnInteger:
        postSet = paginator.page(1)
    except EmptyPage:
        postSet = paginator.page(paginator,num_pages)

    return render(request, "network/profile.html", {
        "profile": profile,
        "followerCount": followerCount,
        "iFollow": iFollow,
        "allPosts": postSet,
        "state": followText
    })

def following(request):
    warning = ''
    friends = Follower.objects.filter(follower = request.user)
    posts = Post.objects.all().order_by('-created_date')
    filteredPosts = []
    for post in posts:
        for friend in friends:
            if friend.star == post.owner:
                filteredPosts.append(post)
    
    if not friends:
        warning = "You are not following anybody."
    
    page = request.GET.get('page', 1)
    paginator = Paginator(filteredPosts, 10)
    try:
        postSet = paginator.page(page)
    except PageNotAnInteger:
        postSet = paginator.page(1)
    except EmptyPage:
        postSet = paginator.page(paginator,num_pages)

    return render(request, "network/following.html", {
        "allPosts": postSet,
        "warning": warning
    })

@csrf_exempt
@login_required
def follow(request):
    followText = ''
    # Retrieve the Data
    data = json.loads(request.body)
    star = data.get("target", "")
    follower = request.user
    profile = User.objects.get(username = star)
    
    follows = Follower.objects.filter(star=profile, follower=follower)
    if not follows:
        following = Follower()
        following.star = profile
        following.follower = follower
        following.save()
        followText = "Unfollow Me"
    else:
        follows.delete()
        followText = "Follow Me"
    
    followerCount = Follower.objects.filter(star = profile).count()
    iFollow = Follower.objects.filter(follower = follower).count()

    return JsonResponse({
        "followText": followText,
        "followerCount": followerCount,
        "iFollow": iFollow,
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

@csrf_exempt
@login_required
def edit(request):
    user = request.user
    # Retrieve the data
    data = json.loads(request.body)
    owner = data.get("user", "")
    content = data.get("content", "")
    postId = data.get("postId", "")
    post = Post.objects.get(pk=postId)
    post.content = content
    post.created_date = datetime.now()
    post.save()

    return JsonResponse({
    "content": content,
    "time": post.created_date
    })

@csrf_exempt
@login_required
def delete(request):
    data = json.loads(request.body)
    postId = data.get("postId", "")
    post = Post.objects.get(pk=postId)
    post.delete()

    return JsonResponse({
    "success": "success"
    })