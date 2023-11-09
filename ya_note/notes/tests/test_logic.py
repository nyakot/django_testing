from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'Slug1'
    NEW_TITLE = 'Обновлённый заголовок заметки'
    NEW_TEXT = 'Обновлённый текст заметки'
    NEW_SLUG = 'new_Slug1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.url_to_add = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }

    def test_author_can_edit_comment(self):
        """4.1 Пользователь может редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_to_add)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

    def test_user_cant_edit_comment_of_another_user(self):
        """4.2 Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)

    def test_author_can_delete_comment(self):
        """4.3 Пользователь может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_add)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        """4.4 Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestCommentCreation(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'Slug1'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.add_url = reverse('notes:add')
        cls.url_to_add = reverse('notes:success')
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_anonymous_user_cant_create_comment(self):
        """1.1 Анонимный пользователь не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_comment(self):
        """1.2 Залогиненный пользователь может создать заметку."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_add)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.slug, self.SLUG)

    def test_empty_slug(self):
        """
        3. Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        self.form_data.pop('slug')
        self.author_client.post(self.add_url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.TITLE))

    def test_user_cant_create_two_equal_slug(self):
        """2. Невозможно создать две заметки с одинаковым slug."""
        note = Note.objects.create(
            title=self.TITLE,
            text=self.TEXT,
            slug=self.SLUG,
            author=self.user
        )
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
