import pytest
from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.mark.django_db
class TestAuthViews:

    def test_register_page_available(self, client):
        response = client.get('/users/register/')
        assert response.status_code == 200

    def test_login_page_available(self, client):
        response = client.get('/users/login/')
        assert response.status_code == 200

    def test_register_user_success(self, client):
        response = client.post('/users/register/', {
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'phone': '+79991112233',
            'birth_date': '1995-05-15',
            'password1': 'testpass123',
            'password2': 'testpass123'})
        assert response.status_code in [302, 200]
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_login_success(self, client, user):
        response = client.post('/users/login/', {
            'username': user.email,
            'password': 'pass123'})
        assert response.status_code in [302, 200]

    def test_login_wrong_password(self, client, user):
        response = client.post('/users/login/', {
            'username': user.email,
            'password': 'wrongpass'})
        assert response.status_code == 200
        assert 'Неверный' in response.content.decode() or b'error' in response.content

@pytest.mark.django_db
class TestAnonymousAccess:

    def test_anonymous_redirected_from_profile(self, client):
        response = client.get('/users/profile/')
        assert response.status_code == 302

    def test_anonymous_can_see_schedule(self, client):
        response = client.get('/schedule/')
        assert response.status_code == 200

    def test_anonymous_can_see_trainers(self, client):
        response = client.get('/trainers/')
        assert response.status_code == 200

    def test_anonymous_can_see_tariffs(self, client):
        response = client.get('/tariffs/')
        assert response.status_code == 200

    def test_anonymous_cannot_book_workout(self, client, schedule):
        response = client.get(f'/schedule/{schedule.id}/book/')
        assert response.status_code == 302
        assert '/users/login/' in response.url

@pytest.mark.django_db
class TestAuthenticatedAccess:

    def test_authenticated_can_access_profile(self, client, user):
        client.force_login(user)
        response = client.get('/users/profile/')
        assert response.status_code == 200

    def test_authenticated_can_see_personal_trainers(self, client, user):
        client.force_login(user)
        response = client.get('/users/personal-trainers/')
        assert response.status_code == 200

    def test_trainer_can_access_dashboard(self, client, trainer):
        client.force_login(trainer)
        response = client.get('/trainers/dashboard/')
        assert response.status_code == 200

    def test_regular_user_cannot_access_trainer_dashboard(self, client, user):
        client.force_login(user)
        response = client.get('/trainers/dashboard/')
        assert response.status_code == 302