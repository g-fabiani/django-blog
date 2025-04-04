from django.urls import path
from . views import PostListView, PostDetailView, PostUpdateView, PostCreateView, PostDeleteView, PostPublishView, PostChangeDateView

app_name = 'blog'
urlpatterns = [
    path('', PostListView.as_view(), name='list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='detail'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='update'),
    path('post/create', PostCreateView.as_view(), name="create"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="delete"),
    path('post/<int:pk>/publish', PostPublishView.as_view(), name="publish"),
    path('post/<int:pk>/change_date', PostChangeDateView.as_view(), name="change_date"),
]