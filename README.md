# Django-blog

Django-blog is a Django application for publishing a blog. Supports creating posts as drafts and programming publication for a future date/time.

## Quick start

1. Add `django_blog` and dependencies to your INSTALLED_APPS setting:
    ```
    INSTALLED_APPS = [
        ...,
        'crispy_forms',
        'crispy_bootstrap5',
        'tinymce',
        'django_blog',
    ]
    ```
2. Include the polls URLconf in your project urls.py:
    ```
    path('blog/', include('django_blog.urls')),
    ```
4. For `crispy-forms`, add the following settings:
    ```
    CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

    CRISPY_TEMPLATE_PACK = 'bootstrap5'

    CRISPY_FAIL_SILENTLY = not DEBUG
    ```
3. Run `python manage.py migrate` to create the models in your database.
4. By default posts are paginated by 4. You can change this adding to your settings:
    ```
    DJANGO_BLOG_PAGINATE_BY = 6
    ```
