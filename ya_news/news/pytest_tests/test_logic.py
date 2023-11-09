from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """1. Анонимный пользователь не может отправить комментарий."""
    client.post(reverse('news:detail', args=[news.pk, ]), data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news, form_data):
    """2. Авторизованный пользователь может отправить комментарий."""
    author_client.post(
        reverse('news:detail', args=[news.pk, ]),
        data=form_data
    )
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == form_data['author']
    assert new_comment.news == form_data['news']


def test_user_cant_use_bad_words(author_client, news):
    """
    3. Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    response = author_client.post(
        reverse('news:detail', args=[news.pk, ]),
        data={'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    )
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news):
    """4.1 Авторизованный пользователь может редактировать свои комментарии."""
    author_client.post(reverse('news:edit', args=[comment.pk, ]), form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == form_data['author']
    assert comment.news == form_data['news']


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        comment
):
    """
    5.1 Авторизованный пользователь не может редактировать чужие
    комментарии.
    """
    response = admin_client.post(
        reverse('news:edit', args=[comment.pk, ]),
        form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == note_from_db.text


def test_author_can_delete_comment(author_client, comment):
    """4.2 Авторизованный пользователь может удалять свои комментарии."""
    author_client.post(reverse('news:delete', args=[comment.pk, ]))
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """
    5.2 Авторизованный пользователь не может удалять чужие
    комментарии.
    """
    response = admin_client.post(reverse('news:delete', args=[comment.pk, ]))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
