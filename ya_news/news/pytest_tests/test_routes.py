from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
    )
)
def test_pages_availability_for_anonymous_user(client, news, name, args):
    """
    1. Главная страница доступна анонимному пользователю.
    2. Страница отдельной новости доступна анонимному пользователю
    6. Страницы регистрации пользователей, входа в учётную запись и выхода из
    неё доступны анонимным пользователям.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    3. Страницы удаления и редактирования комментария доступны автору
    комментария.
    5. Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
        ('news:edit'),
    ),
)
def test_redirects(client, comment, name):
    """
    4. При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
