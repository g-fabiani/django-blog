from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.timezone import now

from .models import Tag, Post

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    model = Post

    list_display = ["title", "pub_date", "update_date"]
    list_filter = ["pub_date"]
    actions = ["publish"]

    @admin.action(description="Pubblica i post selezionati")
    def publish(self, request, queryset):
        queryset.update(pub_date = now())



admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
