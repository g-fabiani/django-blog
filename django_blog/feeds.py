from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.conf import settings

from . models import Post


class RssPostsFeed(Feed):
    description_template = "blog/feeds_description.html"

    def title(self):
        try:
            return settings.DJANGO_BLOG_FEED_TITLE
        except AttributeError:
            return "Generic title"

    def description(self):
        try:
            return settings.DJANGO_BLOG_FEED_DESCRIPTION
        except AttributeError:
            return "Generic description"

    def link(self):
        return reverse("blog:list")

    def items(self):
        return Post.published_objects.order_by("-pub_date")[:100]

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.pub_date
