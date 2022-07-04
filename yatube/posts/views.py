from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import paginator


def index(request):
    '''
    Направит на шаблон 'posts/index.html' с паджинатором
    по всем постам в базе данных.
    '''
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''
    Направит на шаблон 'posts/group_list.html' с паджинатором
    по всем постам группы group_id=slug и объектом этой группы.
    '''
    group_object = get_object_or_404(Group, slug=slug)
    post_list = group_object.posts.select_related('author').all()
    page_obj = paginator(request, post_list)
    context = {
        'group': group_object,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''
    Направит на шаблон 'posts/profile.html' с паджинатором
    по всем постам автора username и объектом этого автора.
    '''
    author_object = get_object_or_404(User, username=username)
    post_list = author_object.posts.select_related(
        'group', 'author').all()
    page_obj = paginator(request, post_list)
    following = None
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author_object)
    context = {
        'page_obj': page_obj,
        'author_object': author_object,
        'following': following
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''
    Направит на шаблон 'posts/post_detail.html' поста с id=post_id
    с объектом этого поста.
    '''
    post_object = get_object_or_404(Post.objects.select_related(
        'group', 'author'), pk=post_id)
    comments = post_object.comments.all()
    if post_object is None:
        raise Http404("Post does not exist")
    count = post_object.author.posts.count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post_object,
        'count': count,
        'comments': comments,
        'form': form
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''
    Направит на шаблон 'posts/create_post.html' создания поста,
    при отправке валидной формы методом POST создаст пост от автора, из
    логина которого совершается отправка формы.
    '''
    form = PostForm(request.POST or None,
                    files=request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    '''
    Направит на шаблон 'posts/create_post.html' редактирования поста, с
    заполненной формой оригинальным содержанием поста post_id,
    при отправки валидной формы методом POST изменит пост от автора, из
    логина которого совершается отправка формы.
    '''
    is_edit = True
    post_object = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_object)
    if request.user != post_object.author:
        raise PermissionDenied
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': is_edit
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post_object = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_object
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_object = get_object_or_404(User, username=username)
    if request.user == author_object:
        return redirect('posts:follow_index')
    if Follow.objects.filter(user=request.user, author=author_object):
        return redirect('posts:follow_index')
    new_follow = Follow(user=request.user, author=author_object)
    new_follow.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author_object = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(user=request.user, author=author_object)
    unfollow.delete()
    return redirect('posts:follow_index')
