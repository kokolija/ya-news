import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, method, args',
    [
        ('news:home', 'GET', None),
        ('news:detail', 'GET', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', 'GET', None),
        ('users:logout', 'POST', None),
        ('users:signup', 'GET', None),
    ]
)
def test_pages_availability_for_anonymous_user(client, name, method, args):
    url = reverse(name, args=args)
    if method == 'GET':
        response = client.get(url)
    else:
        response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_pages_availability_for_comment_edit_and_delete(
        parametrized_client, expected_status, comment, name):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_redirect_for_anonymous_client(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
