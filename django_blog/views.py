from typing import Any
from django.db.models import F
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import now
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.conf import settings
from . models import Post, Tag
from . forms import PostUpdateForm, PostCreateForm, PostChangeDateForm


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.warning(self.request, "È necessario compiere l'accesso per procedere")
        return super().handle_no_permission()


# Create your views here.
class UserCanChangePostMixin(UserPassesTestMixin):
    def test_func(self) -> bool | None:
        self.object = get_object_or_404(Post, pk=self.kwargs['pk'])
        return self.object.can_be_modified_by(self.request.user)

    def handle_no_permission(self) -> HttpResponseRedirect:
        try:
            error_message = f"Non hai le autorizzazioni necessarie per {self.verb} questo post"
        except AttributeError:
            error_message = f"Non hai le autorizzazioni necessarie per compiere questa operazione"

        messages.add_message(self.request, messages.ERROR, error_message)
        return HttpResponseRedirect(self.object.get_absolute_url())


class PostPermissionMixin(UserCanChangePostMixin, CustomLoginRequiredMixin):
    """Mixing handling permissions on operations on posts (updating, deleting, publishing)"""
    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.user.is_authenticated:
            return UserCanChangePostMixin.handle_no_permission(self)
        return CustomLoginRequiredMixin.handle_no_permission(self)


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 4
    try:
        paginate_by = settings.DJANGO_BLOG_PAGINATE_BY
    except AttributeError:
        pass

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = "Blog"
        # Display only tags used in at least one published post
        context['tags'] = Tag.objects.filter(post__pub_date__lte=now()).distinct().order_by('name');
        return context

    def get_queryset(self) -> QuerySet[Any]:
        # Solo gli utenti autenticati possono vedere post
        # non pubblicati
        if self.request.user.is_authenticated:
            queryset = super().get_queryset()
        else:
            queryset = self.model.published_objects.all()

        # Posts are orderd by descendig publication date with drafts first
        return queryset.order_by(F('pub_date').desc(nulls_first=True))


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context

    def get_queryset(self) -> QuerySet[Any]:
        # Solo gli utenti autenticati possono vedere i post
        # non pubblicati
        if self.request.user.is_authenticated:
            return super().get_queryset()
        else:
            return self.model.published_objects.all()


class PostUpdateView(PostPermissionMixin, UpdateView):
    model = Post
    template_name = 'blog/post_update.html'
    form_class = PostUpdateForm

    def __init__(self, **kwargs: Any) -> None:
        self.verb = "modificare"
        super().__init__(**kwargs)


    def get_context_data(self, **kwargs):
        """
        Pass all tags to context in order to render the tag form
        """
        context = super().get_context_data(**kwargs)
        context['tags'] = list(Tag.objects.values())
        context['post_tags'] = list(self.object.tags.values())
        return context

    def form_valid(self, form):
        # Save post
        self.object = form.save()
        # Remove all tags from post
        self.object.tags.clear()
        # Add selected tags
        for name in self.request.POST.getlist('tags'):
            try:
                self.object.tags.create(name=name)
                # Handle existing tags
            except IntegrityError:
                tag = Tag.objects.get(name=name)
                self.object.tags.add(tag)

        messages.add_message(self.request, messages.SUCCESS, f"Hai modificato con successo il post “{form.instance}”")
        return HttpResponseRedirect(self.get_success_url())


class PostCreateView(CustomLoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm

    def get_context_data(self, **kwargs):
        """
        Pass all tags to context in order to render the tag form
        """
        context = super().get_context_data(**kwargs)
        context['tags'] = list(Tag.objects.values())
        context['post_tags'] = []
        return context

    def form_valid(self, form):
        # Set current user to author, if so desired
        if self.request.POST.get("author"):
            form.instance.author = self.request.user

        # Set publication date to current time and date if the post is published
        if self.request.POST.get("submit") == "publish":
            form.instance.pub_date = now()
            message = f"Hai pubblicato il post “{form.instance}”"
            message_level = messages.SUCCESS

        # Make the user set the date manually if they wish to schedule the post
        elif self.request.POST.get("submit") == "set_date":
            self.object = form.save()
            message = "Se decidi di annullare questa operazione, il post verrà salvato come bozza"
            message_level = messages.INFO
            self.success_url = reverse(
                'blog:change_date',
                kwargs={'pk': form.instance.pk}
                )

        # Else save the post as draft
        else:
            message = f"Hai salvato in bozze il post “{form.instance}”"
            message_level = messages.SUCCESS

        # Save post
        self.object = form.save()

        # Remove all tags
        self.object.tags.clear()
        # Add selected tags
        for name in self.request.POST.getlist('tags'):
            try:
                self.object.tags.create(name=name)
            # Handle existing tags
            except IntegrityError:
                tag = Tag.objects.get(name=name)
                self.object.tags.add(tag)

        # Redirect to the correct page with correct message
        messages.add_message(self.request, message_level, message)
        return HttpResponseRedirect(self.get_success_url())


class PostDeleteView(PostPermissionMixin, DeleteView):
    model = Post
    template_name = "blog/post_delete.html"
    success_url = reverse_lazy('blog:list')

    def __init__(self, **kwargs: Any) -> None:
        self.verb = "eliminare"
        super().__init__(**kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        post = self.get_object()
        response = super().post(request, *args, **kwargs)
        messages.add_message(self.request, messages.ERROR, f"Hai eliminato il post “{post}”")
        return response

class PostPublishView(PostPermissionMixin, UserPassesTestMixin, View):

    def __init__(self, **kwargs: Any) -> None:
        self.verb = "pubblicare"
        super().__init__(**kwargs)

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        post.publish()
        messages.add_message(request, messages.SUCCESS, f"Hai pubblicato il post “{post}”")
        return HttpResponseRedirect(post.get_absolute_url())

    def test_func(self) -> bool | None:
        """It should be possible to publish only posts that are not already published"""
        if super().test_func():
            return not self.object.is_published()


class PostChangeDateView(PostPermissionMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "blog/post_change_date.html"
    form_class = PostChangeDateForm

    def form_valid(self, form) -> HttpResponse:
        response =  super().form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, f"Hai programmato la pubblicazione del post “{self.get_object()}”")
        return response

    def test_func(self) -> bool | None:
        """It should be possible to change date only for posts not already published"""
        if super().test_func():
            return not self.object.is_published()


class PostListByTagView(ListView):
    model = Post
    template_name = "blog/post_list_by_tag.html"
    context_object_name = "posts"
    paginate_by = 4
    try:
        paginate_by = settings.DJANGO_BLOG_PAGINATE_BY
    except AttributeError:
        pass

    def get_queryset(self, **kwargs):
        return self.model.published_objects.filter(tags__pk=self.kwargs['pk']).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(pk=self.kwargs['pk'])
        return context