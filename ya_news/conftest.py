from datetime import datetime, timedelta
import time

from django.conf import settings
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def news_list():
    news_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news_item = News.objects.create(
            title=f'Заголовок {i}',
            text=f'Текст заметки {i}',
            date=datetime.today() - timedelta(days=i),
        )
        news_list.append(news_item)
    return news_list


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comment_list(author, news):
    comment_list = []
    for i in range(2):
        comment_item = Comment.objects.create(
            text=f'Текст комментария {i}',
            author=author,
            news=news,
            created=timezone.now()
        )
        comment_list.append(comment_item)
        time.sleep(0.1)
    return comment_list


@pytest.fixture
def news_pk_for_args(news):
    return news.pk,


@pytest.fixture
def form_data(author, news):
    return {
        'text': 'Новый текст',
        'author': author,
        'news': news,
    }


@pytest.fixture
def home_url():
    return 'news:home'


@pytest.fixture
def login_url():
    return 'users:login'


@pytest.fixture
def logout_url():
    return 'users:logout'


@pytest.fixture
def signup_url():
    return 'users:signup'
