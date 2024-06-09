from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post


class PostListView(ListView):
    """
    Class based view to list all the posts
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# Create your views here.
def post_list(request, tag_slug=None):
    """
    View to list all the posts
    :param request:
    :param tag_slug:
    :return:
    """
    _posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        _posts = _posts.filter(tags__in=[tag])
    paginator_posts = Paginator(_posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator_posts.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator_posts.get_page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator_posts.get_page(paginator_posts.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    """
    View to display a single post
    :param request:
    :param post:
    :param day:
    :param month:
    :param year:
    :return:
    """
    post = get_object_or_404(Post, publish__year=year, publish__month=month, publish__day=day, slug=post,
                             status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html',
                  {'post': post, 'comments': comments, 'form': form, "similar_posts": similar_posts})


def custom_error_view(request, exception=None):
    return render(request, "blog/errors/404.html", {})


def post_share(request, post_id):
    """
    View to share a post via email
    :param request:
    :param post_id:
    :return:
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (f"{cd['name']} ({cd['email']}) "
                       f"recommends you reading {post.title}")
            message = (f"Read {post.title} at {post_url}\n\n"
                       f"{cd['name']}'s comments: {cd['comments']}")
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    """
    View to post a comment
    :param request:
    :param post_id:
    :return:
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'comment': comment, 'form': form})


def post_search(request):
    """
    View to search for posts
    :param request:
    :return:
    """
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A', config='spanish') + SearchVector('body', weight='B',
                                                                                               config='spanish')
            search_query = SearchQuery(query, config='spanish')
            results = Post.published.annotate(search=search_vector,
                                              rank=SearchRank(search_vector, search_query)).filter(
                rank__gte=0.3).order_by('-rank')
            print(results)
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
