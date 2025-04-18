from django.test import TestCase
from . models import Post, Tag
from django.utils.timezone import now
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.test import MessagesTestMixin
from django.contrib import messages
from django.contrib.messages.storage.base import Message
import datetime

# Create your tests here.
DATEFORMAT = "%Y-%m-%dT%H:%M"

class PostPopulatedTestCase(TestCase):
    def setUp(self) -> None:
        """Make some posts: published scheduled and drafs"""

        # Post with publication date in the past
        self.pub_post = Post.objects.create(
            title="Published post",
            subtitle="Subtitle of published post",
            body="Body of published post",
            pub_date=now() - datetime.timedelta(days=1)
        )

        # Post with publication date in the future
        self.future_post = Post.objects.create(
            title="Future post",
            subtitle="Subtitle of future post",
            body="Body of future post",
            pub_date=now() + datetime.timedelta(days=1)
        )

        # Post with no publication date
        self.draft_post = Post.objects.create(
            title="Draft post",
            subtitle="Subtitle of draft post",
            body="Body of draft post"
        )



class PostModelTest(PostPopulatedTestCase):
    """Test for Post model and relative methods"""
    def test_post_title(self):
        self.assertEqual(f"{self.pub_post.title}", "Published post")

    def test_post_subtitle(self):
        self.assertEqual(f"{self.pub_post.subtitle}", "Subtitle of published post")

    def test_post_body(self):
        self.assertEqual(f"{self.pub_post.body}", "Body of published post")

    def test_post_publish_method(self):
        self.draft_post.publish()
        self.assertLessEqual(self.draft_post.pub_date, now())
        self.future_post.publish()
        self.assertLessEqual(self.draft_post.pub_date, now())

    def test_post_is_draft_method(self):
        self.assertFalse(self.pub_post.is_draft())
        self.assertFalse(self.future_post.is_draft())
        self.assertTrue(self.draft_post.is_draft())

    def test_post_is_published_method(self):
        self.assertTrue(self.pub_post.is_published())
        self.assertFalse(self.future_post.is_published())
        self.assertFalse(self.draft_post.is_published())

    def test_post_published_objects(self):
        self.assertEqual(Post.published_objects.count(), 1)
        self.future_post.publish()
        self.assertEqual(Post.published_objects.count(), 2)

    def test_post_objects(self):
        self.assertEqual(Post.objects.count(), 3)

    def test_get_days_from_publication_to_update_past_post(self):
        self.assertEqual(self.pub_post.get_days_from_publication_to_update(), 1)

    def test_get_days_from_publication_to_update_future_post(self):
        self.assertEqual(self.future_post.get_days_from_publication_to_update(), 0)

    def test_get_days_from_publication_to_update_draf(self):
        self.assertEqual(self.draft_post.get_days_from_publication_to_update(), 0)


class PostViewEmptyTest(TestCase):
    def test_post_list_vew_url_by_name(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)

    def post_list_view_url_location(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_view_template(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_list_queryset(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['posts'], [])


class PostViewPopulatedTest(PostPopulatedTestCase):

    def setUp(self) -> None:
        super().setUp()
        get_user_model().objects.create_user('test', password='test').save()

    def test_post_list_view_url_by_name(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)

    def test_post_list_view_url_location(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_view_template(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_list_view_queryset(self):
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['posts'], [self.pub_post])

    def test_post_list_view_auth_queryset(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code , 200)
        self.assertQuerySetEqual(
            response.context['posts'],
            [self.draft_post, self.future_post, self.pub_post]
        )

    def test_published_detail_view_by_name(self):
        response = self.client.get(self.pub_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_published_detail_view_location(self):
        response = self.client.get(f'/blog/post/{self.pub_post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_published_detail_view_template(self):
        response = self.client.get(self.pub_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_unpublished_detail_view_404(self):
        response = self.client.get(self.future_post.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.draft_post.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_unpublished_detail_view_auth(self):
        self.client.login(username='test', password='test')
        response = self.client.get(self.future_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.draft_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class PostDeleteTest(MessagesTestMixin, PostPopulatedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = get_user_model().objects.create(username="test", password="test")

    def test_delete_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)

    def test_delete_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confermi di voler eliminare il post")

    def test_delete_has_effect(self):
        self.assertEqual(Post.objects.count(), 3)
        self.client.force_login(self.user)
        response = self.client.post(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 2)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, pk=self.pub_post.pk)

    def test_delete_redirect_correct_page(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.url, reverse('blog:list'))

    def test_delete_unauth_redirects_to_login(self):
        response = self.client.post(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 3)

    def test_delete_message(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('blog:delete', kwargs={'pk': self.pub_post.pk}))
        self.assertMessages(response, [Message(messages.ERROR, f"Hai eliminato il post “{self.pub_post}”")])


class PostPublishTest(MessagesTestMixin, PostPopulatedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = get_user_model().objects.create(
            username='test1',
            password='test1'
            )
        self.user2 = get_user_model().objects.create(
            username='test2',
            password='test2'
            )

        self.future_post2 = Post.objects.create(
            title="Future post user 2",
            subtitle="Subtitle of future post user 2",
            body="Body of future post user 2",
            author=self.user2
        )

    def test_publish_view_by_name(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.draft_post.pk}))
        self.assertEqual(response.status_code, 302)

    def test_publish_has_effect_on_draft(self):
        self.assertTrue(self.draft_post.is_draft())
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.draft_post.pk}))
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.draft_post.pk)
        self.assertFalse(post.is_draft())

    def test_publish_has_effect_on_future_post(self):
        self.assertFalse(self.future_post.is_published())
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post.pk}))
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.future_post.pk)
        self.assertTrue(post.is_published())

    def test_cannot_publish_published_post(self):
        self.client.force_login(self.user1)
        og_pub_date = self.pub_post.pub_date
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.pub_post.pk)
        self.assertEqual(og_pub_date, post.pub_date)

    def test_can_publish_own_post(self):
        self.assertFalse(self.future_post2.is_published())
        self.client.force_login(self.user2)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post2.pk}))
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.future_post2.pk)
        self.assertTrue(post.is_published())

    def test_cannot_publish_another_users_post(self):
        self.assertFalse(self.future_post2.is_published())
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post2.pk}))
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.future_post2.pk)
        self.assertFalse(post.is_published())

    def test_cannot_publish_another_users_post_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post2.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.ERROR, "Non hai le autorizzazioni necessarie per pubblicare questo post")])

    def test_publish_redirect_correct_page(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.future_post.get_absolute_url())

    def test_publish_unauth_redirects_to_login(self):
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post.pk}))
        self.assertEqual(response.status_code, 302)

    def test_publish_success_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('blog:publish', kwargs={'pk': self.future_post.pk}))
        self.assertMessages(response, [Message(messages.SUCCESS, f"Hai pubblicato il post “{self.future_post}”")])


class PostChangeDateTest(MessagesTestMixin, PostPopulatedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = get_user_model().objects.create(username="test1",  password="test1")
        self.user2 = get_user_model().objects.create(username="test2", password="test2")

        self.draft_post2 = Post.objects.create(
            title="Future post user 2",
            subtitle="Subtitle of future post user 2",
            body="Body of future post user 2",
            author=self.user2
        )

        self.new_pub_date = now() + datetime.timedelta(days=7)


    def test_change_date_view_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_change_date_view_template(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_change_date.html')

    def test_change_date_view_post(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)

    def test_change_date_view_post_redirect_correct_page(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.draft_post.get_absolute_url())

    def test_change_date_has_effect_on_draft(self):
        self.assertTrue(self.draft_post.is_draft())
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.draft_post.pk)
        self.assertFalse(post.is_draft())

    def test_change_date_has_effect_on_future_post(self):
        og_pub_date = self.future_post.pub_date;
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.future_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.future_post.pk)
        self.assertNotEqual(post.pub_date.strftime(DATEFORMAT), og_pub_date.strftime(DATEFORMAT))

    def test_change_date_success_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.SUCCESS, f"Hai programmato la pubblicazione del post “{self.draft_post}”")])

    def test_cannot_change_date_of_published_post(self):
        self.assertTrue(self.pub_post.is_published())
        self.client.force_login(self.user1)
        response = self.client.get(reverse('blog:change_date', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.pub_post.get_absolute_url())

    def test_cannot_change_date_of_published_post_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.pub_post.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.ERROR, "Non hai le autorizzazioni necessarie per compiere questa operazione")])

    def test_cannot_change_date_of_another_users_post(self):
        self.client.force_login(self.user1)
        self.assertTrue(self.draft_post2.is_draft())
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post2.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        # Check publication date of post was not set
        post = Post.objects.get(pk=self.draft_post2.pk)
        self.assertTrue(post.is_draft())

    def test_cannot_change_date_of_another_users_post_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:change_date', kwargs={'pk': self.draft_post2.pk}),
            {'pub_date': self.new_pub_date.strftime(DATEFORMAT)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.ERROR, "Non hai le autorizzazioni necessarie per compiere questa operazione")])

    def test_change_date_unauth_redirects_to_login(self):
        response = self.client.get(reverse('blog:change_date', kwargs={'pk': self.draft_post.pk}))
        self.assertEqual(response.status_code, 302)


class PostUpdateTest(MessagesTestMixin, PostPopulatedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = get_user_model().objects.create(username="test1",  password="test1")
        self.user2 = get_user_model().objects.create(username="test2", password="test2")

        self.draft_post2 = Post.objects.create(
            title="Future post user 2",
            subtitle="Subtitle of future post user 2",
            body="Body of future post user 2",
            author=self.user2
        )

        self.og_tag = Tag.objects.create(name='tag')

        self.post_tag = Post.objects.create(
            title='Post with tag',
            body='Body of post with tag',
        )
        self.post_tag.tags.add(self.og_tag)

    def test_update_view_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('blog:update', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_view_template(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('blog:update', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_update.html')

    def test_update_view_post(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.pub_post.pk}),
            {
                'title': self.pub_post.title,
                'body': str(self.pub_post.body) + " updated"
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_update_view_post_redirect_correct_page(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.pub_post.pk}),
            {
                'title': self.pub_post.title,
                'body': str(self.pub_post.body) + " updated"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.pub_post.get_absolute_url())

    def test_update_has_effect_on_post(self):
        self.client.force_login(self.user1)
        updated_body = str(self.pub_post.body) + " updated"
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.pub_post.pk}),
            {
                'title': self.pub_post.title,
                'body': updated_body
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.pub_post.pk)
        self.assertEqual(post.body, updated_body)

    def test_update_success_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.pub_post.pk}),
            {
                'title': self.pub_post.title,
                'body': str(self.pub_post.body) + " updated"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.SUCCESS, f"Hai modificato con successo il post “{self.pub_post.title}”")])

    def test_cannot_update_another_users_post(self):
        self.client.force_login(self.user1)
        og_body = str(self.draft_post2.body)
        updated_body = og_body + " updated"
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.draft_post2.pk}),
            {
                'title': self.draft_post2.title,
                'body': updated_body
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(pk=self.draft_post2.pk)
        # Assert post body was not changed
        self.assertNotEqual(post.body, updated_body)
        self.assertEqual(post.body, og_body)

    def test_cannot_update_another_users_post_message(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.draft_post2.pk}),
            {
                'title': self.draft_post2.title,
                'body': str(self.draft_post2.body) + " updated"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.ERROR, "Non hai le autorizzazioni necessarie per modificare questo post")])

    def test_update_unauth_redirects_to_login(self):
        response = self.client.get(reverse('blog:update', kwargs={'pk': self.pub_post.pk}))
        self.assertEqual(response.status_code, 302)

    def test_update_post_adding_tag(self):
        self.client.force_login(self.user1)
        tag_name = 'tag 1'
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.pub_post.pk}),
            {
                'title': self.pub_post.title,
                'body': self.pub_post.body,
                'tags': [tag_name]
            }
        )
        self.assertEqual(response.status_code, 302)
        tag = Tag.objects.get(name=tag_name)
        self.assertEqual(self.pub_post.tags.first().pk, tag.pk)

    def test_update_post_changing_tag(self):
        self.client.force_login(self.user1)
        tag_name = 'tag 1'
        response = self.client.post(
            reverse('blog:update', kwargs={'pk': self.post_tag.pk}),
            {
                'title': self.post_tag.title,
                'body': self.post_tag.body,
                'tags': [tag_name]
            }
        )
        self.assertEqual(response.status_code, 302)
        tag = Tag.objects.get(name=tag_name)
        self.assertNotEqual(self.post_tag.tags.first().pk, self.og_tag.pk)
        self.assertEqual(self.post_tag.tags.first().pk, tag.pk)


class PostCreateTest(MessagesTestMixin, TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="test", password="test")
        super().setUp()

    def test_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 200)

    def test_create_view_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_create.html')

    def test_create_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body'
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_create_has_effect(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)

    def test_create_redirect_correct_page(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertEqual(response.url, post.get_absolute_url())

    def test_create_post_as_draft(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'draft'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertTrue(post.is_draft())

    def test_create_post_as_draft_message(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'draft'
            }
        )
        post = Post.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.SUCCESS, f"Hai salvato in bozze il post “{post}”")])

    def test_create_post_with_author(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'author': 'true'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)

    def test_create_post_and_publish(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'publish'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertTrue(post.is_published())

    def test_create_post_and_publish_message(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'publish'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertMessages(response, [Message(messages.SUCCESS, f"Hai pubblicato il post “{post}”")])

    def test_create_post_and_program(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'set_date'
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertTrue(post.is_draft())
        self.assertEqual(response.url, reverse('blog:change_date', kwargs={'pk': post.pk}))

    def test_create_post_and_program_message(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('blog:create'),
            {
                'title': 'New post title',
                'body': 'New post body',
                'submit': 'set_date'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertMessages(response, [Message(messages.INFO, "Se decidi di annullare questa operazione, il post verrà salvato come bozza")])

    def test_create_unauth_redirects_to_login(self):
        response = self.client.get(reverse('blog:create'))
        self.assertEqual(response.status_code, 302)

    def test_create_post_with_tag(self):
        self.client.force_login(self.user)
        tag_name = 'tag 1'
        response = self.client.post(
            reverse('blog:create'),
            {
            'title': 'New post title',
            'body': 'New post body',
            'tags': [tag_name]
            }
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        tag = Tag.objects.get(name=tag_name)
        self.assertEqual(post.tags.first().pk, tag.pk)

class PostByTagViewTest(PostPopulatedTestCase):
    def setUp(self):
        super().setUp()
        # Add some other published posts
        self.pub_post2 = Post.objects.create(
            title="Published post 2",
            subtitle="Subtitle of published post 2",
            body="Body of published post 2",
            pub_date=now() - datetime.timedelta(days=1)
        )
        self.pub_post3 = Post.objects.create(
            title="Published post 3",
            subtitle="Subtitle of published post 3",
            body="Body of published post 3",
            pub_date=now() - datetime.timedelta(days=1)
        )

        # Add some tags to posts
        self.tag1 = Tag.objects.create(name="tag 1")
        self.tag2 = Tag.objects.create(name="tag 2")
        self.tag3 = Tag.objects.create(name="tag 3")
        self.tag4 = Tag.objects.create(name="tag 4")
        self.tag5 = Tag.objects.create(name="tag 5")

        self.pub_post.tags.add(self.tag1)
        self.pub_post.tags.add(self.tag2)

        self.pub_post2.tags.add(self.tag2)

        self.pub_post3.tags.add(self.tag2)

        self.future_post.tags.add(self.tag3)
        self.future_post.tags.add(self.tag1)

        self.draft_post.tags.add(self.tag5)

    def test_post_list_view_tags_queryset(self):
        """only tags associated with published posts"""
        response = self.client.get(reverse('blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['tags'], [self.tag1, self.tag2])

    def test_post_list_by_tag_view_url_by_name(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={'pk': self.tag1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_list_by_tag_view_url_location(self):
        response = self.client.get(f'/blog/tag/{self.tag1.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_post_list_by_tag_view_404(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={'pk': 100}))
        self.assertEqual(response.status_code, 404)

    def test_post_list_by_tag_view_template(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={'pk': self.tag1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('blog/post_list_by_tag.html')

    def test_post_list_by_tag_queryset(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={'pk': self.tag1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], [self.pub_post])
        self.assertEqual(response.context['tag'], self.tag1)

    def test_post_list_by_tag_empty_queryset_unpublished(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={"pk": self.tag3.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['posts'], [])
        self.assertEqual(response.context['tag'], self.tag3)

    def test_post_list_by_tag_empty_queryset_unused(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={'pk': self.tag4.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], [])
        self.assertEqual(response.context['tag'], self.tag4)

    def test_post_list_by_tag_queryset_multiple_posts(self):
        response = self.client.get(reverse('blog:list_by_tag', kwargs={"pk": self.tag2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], [self.pub_post3, self.pub_post2, self.pub_post])
        self.assertEqual(response.context['tag'], self.tag2)

class FeedRssTest(TestCase):
    def test_rss_view_by_name(self):
        response = self.client.get(reverse('blog:feed_rss'))
        self.assertEqual(response.status_code, 200)

    def test_rss_view_by_url(self):
        response = self.client.get('/blog/feed/rss/')
        self.assertEqual(response.status_code, 200)
