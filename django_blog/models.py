from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now


class PublishedPostManager(models.Manager):
    """
    Un manager per i post che restituisce solamente
    i post la pubblicati (con data di pubblicazione non
    precedente al giorno corrente)
    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(pub_date__lte=now())


class Tag(models.Model):
    """Modella un tag. Ha come unica proprietà il nome del tag"""
    name = models.CharField("nome",
                            max_length=60,
                            null=False,
                            blank=False,
                            unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'tag'


class Post(models.Model):
    "Modella un post sul blog"
    title = models.CharField("titolo", max_length=100, null=False, blank=False)
    subtitle = models.CharField(
        "sottotitolo", max_length=200, null=True, blank=True)
    body = models.TextField("testo", null=False, blank=False)
    pub_date = models.DateTimeField(
        "data di pubblicazione", null=True, blank=True)
    # Update date is set every time the object is saved
    update_date = models.DateTimeField(
        'ultima modifica',
        auto_now=True
    )
    author = models.ForeignKey(
        verbose_name="autore",
        to=get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True
    )

    objects = models.Manager()
    published_objects = PublishedPostManager()

    def publish(self):
        self.pub_date = now()
        self.save()

    def can_be_modified_by(self, user):
        return not self.author or self.author == user

    def is_published(self):
        datetime = now()
        return (not self.is_draft()) and (self.pub_date <= datetime)

    def get_days_from_publication_to_update(self):
        """
        Return the number of days elapsed between the publication
        and the last update of the post
        """
        if self.is_published():
            delta = self.update_date - self.pub_date
            return delta.days
        else:
            return 0

    def is_draft(self):
        return self.pub_date is None

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = 'post'
