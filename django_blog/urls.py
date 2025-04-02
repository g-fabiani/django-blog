from django.urls import path
from . views import PostListView, PostDetailView, PostUpdateView, PostCreateView, PostDeleteView, PostPublishView, PostChangeDateView

urlpatterns = [
    path('', PostListView.as_view(), name='posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post_update'),
    path('post/create', PostCreateView.as_view(), name="post_create"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="post_delete"),
    path('post/<int:pk>/publish', PostPublishView.as_view(), name="post_publish"),
    path('post/<int:pk>/change_date', PostChangeDateView.as_view(), name="post_change_date"),
]