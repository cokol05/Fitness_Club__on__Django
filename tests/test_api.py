import pytest

@pytest.mark.django_db
class TestApiEndpoints:

    def test_api_root(self, client):
        response = client.get('/api/v1/')
        assert response.status_code == 200

    def test_workout_list_api(self, client, workout):
        response = client.get('/api/v1/workouts/')
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_schedule_list_api(self, client, schedule):
        response = client.get('/api/v1/schedules/')
        assert response.status_code == 200

    def test_tariff_list_api(self, client, tariff):
        response = client.get('/api/v1/tariffs/')
        assert response.status_code == 200

    def test_trainer_list_api(self, client, trainer_bio):
        response = client.get('/api/v1/trainers/')
        assert response.status_code == 200