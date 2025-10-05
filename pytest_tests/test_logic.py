import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id_for_args, comment_form_data):
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        not_author_client, news_id_for_args, comment_form_data):
    url = reverse('news:detail', args=news_id_for_args)
    not_author_client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']


def test_user_cant_use_bad_words(not_author_client, news_id_for_args):
    bad_words_data = {'text': f'Начало, {BAD_WORDS[0]}, конец'}
    url = reverse('news:detail', args=news_id_for_args)
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    old_count = Comment.objects.count()
    author_client.delete(url)
    assert Comment.objects.count() == old_count - 1


def test_author_can_edit_comment(
        author_client, comment, comment_id_for_args, comment_form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    author_client.post(url, data=comment_form_data)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_id_for_args):
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, comment_id_for_args, comment_form_data):
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_form_data['text']
