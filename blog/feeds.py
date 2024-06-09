import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy

from .models import Post


class LatestPostFeeds(Feed):
    """
    Feed class for the latest posts
    """
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'

    def items(self):
        """
        Return the latest 5 published posts
        :return:
        """
        return Post.published.all()[:5]

    def item_title(self, item):
        """
        Return the title of the post
        :param item:
        :return:
        """
        return item.title

    def item_description(self, item):
        """
        Return the description of the post
        :param item:
        :return:
        """
        html_content = markdown.markdown(item.body)
        truncated_content = truncatewords(html_content, 30)
        return truncated_content

    def item_link(self, item):
        """
        Return the URL of the post
        :param item:
        :return:
        """
        return item.get_absolute_url()

    def item_pubdate(self, item):
        """
        Return the publication date of the post
        :param item:
        :return:
        """
        return item.publish
