from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('login_url'), None),
        (pytest.lazy_fixture('logout_url'), None),
        (pytest.lazy_fixture('signup_url'), None),
        (pytest.lazy_fixture('home_url'), None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
    )
)
def test_pages_availability_for_anonymous_user(client, news, name, args):
    """
    1. Главная страница доступна анонимному пользователю.
    2. Страница отдельной новости доступна анонимному пользователю
    6. Страницы регистрации пользователей, входа в учётную запись и выхода из
    неё доступны анонимным пользователям.
    """
    response = client.get(reverse(name, args=args))
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
    response = parametrized_client.get(reverse(name, args=(comment.pk,)))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
        ('news:edit'),
    ),
)
def test_redirects(client, comment, name, login_url):
    """
    4. При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    url = reverse(name, args=(comment.pk,))
    response = client.get(url)
    assertRedirects(response, f'{reverse(login_url)}?next={url}')
