import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_and_order(client):
    today = datetime.today()
    url = reverse('news:home')
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count < settings.NEWS_COUNT_ON_HOME_PAGE + 1
    assert all_dates == sorted_dates


def test_comments_order(client, not_author, news, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    news.date -= timedelta(days=9)
    for index in range(7):
        comment = Comment.objects.create(
            news=news,
            text=f'Комментарий {index}',
            author=not_author
        )
        comment.created = news.date + timedelta(days=index)
        comment.save()
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = not_author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
