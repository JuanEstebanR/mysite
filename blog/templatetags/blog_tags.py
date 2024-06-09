from django import template
import markdown
from django.utils.safestring import mark_safe
from django.db.models import Count
from ..models import Post

register = template.Library()


@register.simple_tag
def total_posts():
    """
    Custom template tag to display the total number of posts
    :return:
    """
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """
    Custom template tag to display the latest posts
    :param count:
    :return:
    """
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """
    Custom template tag to display the most commented posts
    :param count:
    :return:
    """
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    """
    Custom template filter to convert markdown to HTML
    :param text:
    :return:
    """
    return mark_safe(markdown.markdown(text))