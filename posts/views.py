from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'posts': posts,
                                          'page': page,
                                          'paginator': paginator, })


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:index')
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=user).exists()
    posts = user.posts.all()
    post_count = user.posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'count': post_count,
        'user_name': user,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=post.author).exists()
    post_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'user_name': post.author,
        'post': post,
        'count': post_count,
        'comments': comments,
        'form': form,
        'following': following,
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('posts:post', post.author, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None, instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/new.html', {'form': form, 'post': post})
    form.save()
    return redirect('posts:post', post.author, post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post_id = post
        new_comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/follow.html', {'page': page,
                                                 'paginator': paginator})


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        Follow.objects.get_or_create(user=request.user, author=user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        Follow.objects.filter(author=user, user=request.user).delete()
    return redirect('posts:profile', username)
