from django.urls import path
from . views import PostListView, PostDetailView, PostUpdateView, PostCreateView, PostDeleteView, PostPublishView, PostChangeDateView, PostListByTagView
from . feeds import RssPostsFeed

app_name = 'blog'
urlpatterns = [
    path('', PostListView.as_view(), name='list'),
    path('tag/<int:pk>/', PostListByTagView.as_view(), name='list_by_tag'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='detail'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='update'),
    path('post/create', PostCreateView.as_view(), name="create"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="delete"),
    path('post/<int:pk>/publish', PostPublishView.as_view(), name="publish"),
    path('post/<int:pk>/change_date', PostChangeDateView.as_view(), name="change_date"),
    path('feed/rss', RssPostsFeed(), name="feed_rss")
]