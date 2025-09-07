from django.shortcuts import render, get_object_or_404
from .models import Blogpost

def index(request):
    myposts = Blogpost.objects.all().order_by('-pub_date')  # latest first
    return render(request, 'blog/index.html', {'myposts': myposts})

def blogpost(request, id):
    post = get_object_or_404(Blogpost, post_id=id)
    return render(request, 'blog/blogpost.html', {'post': post})
