from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    """
    Sitemap for posts
    """
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        """
        Return published posts
        :return:
        """
        return Post.published.all()

    @staticmethod
    def lastmod(obj):
        """
        Return the last time the post was modified
        :param obj:
        :return:
        """
        return obj.updated
