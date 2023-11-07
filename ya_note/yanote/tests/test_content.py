from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'Slug1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_notes_list_for_different_users(self):
        """
        1. отдельная заметка передаётся на страницу со списком заметок в
        списке object_list, в словаре context.
        2. в список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        users = (
            self.author,
            self.reader,
        )
        for user in users:
            self.client.force_login(user)
            response = self.client.get(self.list_url)
            object_list = response.context['object_list']
            with self.subTest(user=user):
                if user == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        """
        3. на страницы создания и редактирования заметки передаются
        формы.
        """
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
