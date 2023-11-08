import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, news_list):
    """1. Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """
    2. Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comment_list, news):
    """
    3. Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=[news.pk, ])
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    """
    4.1 Авторизованному пользователю доступна форма для отправки комментария
    на странице отдельной новости.
    """
    url = reverse('news:detail', args=[news.pk, ])
    response = author_client.get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """
    4.2 Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости.
    """
    url = reverse('news:detail', args=[news.pk, ])
    response = client.get(url)
    assert 'form' not in response.context
