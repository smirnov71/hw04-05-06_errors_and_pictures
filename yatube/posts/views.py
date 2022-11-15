from .models import Post, Group, User, Comment
from django.shortcuts import redirect, render, get_object_or_404
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .utils import paginate_page

# Create your views here.


def index(request):
    # Получаем набор записей для страницы с запрошенным номером
    posts = Post.objects.select_related("group", "author")
    page_obj = paginate_page(request, posts)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    # paginator = Paginator(post_list, 10)
    # page_number = request.GET.get('page')
    page_obj = paginate_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("author")
    page_obj = paginate_page(request, posts)

    context = {
        'author': author,
        'page_obj': page_obj,
        'following':True
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    # Получаем набор комментариев для поста с запрошенным номером
    comments = Comment.objects.select_related("post")
    context = {
        'post': post,
        'author': author,
        'form': CommentForm(request.POST or None),
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
    return render(request, template, {'form': form, 'is_edit': False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post_id and request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)

@login_required
def add_comment(request, post_id):
    # Получите пост
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=request.user
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)



@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    context = {}
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    # Подписаться на автора
    ...

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    ...
 
