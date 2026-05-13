import pytest

""""(MAIN VIEWS) проверяют, что основные страницы сайта открываются"""

@pytest.mark.django_db
class TestMainViews:
    """Тесты главных страниц сайта"""
    def test_home_page_status(self, client):
        """
        Проверка: Главная страница открывается (статус 200)
        Ожидание: GET запрос к '/' возвращает HTTP 200 OK
        """
        response = client.get('/')
        assert response.status_code == 200  # 200 = страница найдена и работает

    def test_home_page_template(self, client):
        """
        Проверка: Главная страница использует правильный шаблон 'home.html'
        Ожидание: В ответе используется шаблон home.html
        """
        response = client.get('/')
        # Проверяем, что среди использованных шаблонов есть home.html
        assert 'home.html' in [t.name for t in response.templates]

    def test_trainer_list_page(self, client, trainer_bio):
        """
        Проверка: Страница списка тренеров открывается
        """
        response = client.get('/trainers/')
        assert response.status_code == 200

    def test_trainer_detail_page(self, client, trainer_bio):
        """
        Проверка: Страница конкретного тренера открывается
        """
        response = client.get(f'/trainers/{trainer_bio.pk}/')
        assert response.status_code == 200

    def test_schedule_list_page(self, client):
        """
        Проверка: Страница расписания открывается
        """
        response = client.get('/schedule/')
        assert response.status_code == 200

    def test_tariff_list_page(self, client):
        """
        Проверка: Страница тарифов открывается
        """
        response = client.get('/tariffs/')
        assert response.status_code == 200

    def test_workout_detail_page(self, client, schedule):
        """
        Проверка: Страница деталей тренировки открывается
        """
        response = client.get(f'/workouts/{schedule.workout.pk}/')
        assert response.status_code == 200


"""(BOOKING VIEWS) проверяют, что пользователи могут записываться и отменять записи"""


@pytest.mark.django_db
class TestBookingViews:
    """Тесты функционала записи на тренировки"""

    def test_anonymous_cannot_book_workout(self, client, schedule):
        response = client.get(f'/schedule/{schedule.id}/book/')
        # 302 = редирект (перенаправление на страницу входа)
        assert response.status_code == 302

    def test_authenticated_can_book_workout_page(self, client, user_with_tariff, schedule):
        # force_login = принудительный вход пользователя
        client.force_login(user_with_tariff)
        response = client.get(f'/schedule/{schedule.id}/book/')
        assert response.status_code == 200

    def test_booking_creates_correctly(self, client, user_with_tariff, schedule):
        """
        Проверка: При POST-запросе создаётся запись в базе данных
        Ожидание: В таблице Booking появляется новая запись
        """
        from main.models import Booking

        client.force_login(user_with_tariff)
        response = client.post(f'/schedule/{schedule.id}/book/')

        # Проверяем, что запись существует в БД
        assert Booking.objects.filter(
            user=user_with_tariff,
            schedule=schedule
        ).exists()

    def test_cannot_book_past_workout(self, client, user_with_tariff, past_schedule):
        """
        Проверка: Нельзя записаться на прошедшую тренировку
        Ожидание: GET запрос возвращает редирект (302)
        """
        client.force_login(user_with_tariff)
        response = client.get(f'/schedule/{past_schedule.id}/book/')
        assert response.status_code == 302

    def test_trainer_cannot_book_own_workout(self, client, trainer, schedule):
        """
        Проверка: Тренер не может записаться на свою же тренировку
        Ожидание: GET запрос возвращает редирект (302)
        """
        client.force_login(trainer)
        response = client.get(f'/schedule/{schedule.id}/book/')
        assert response.status_code == 302



"""(TRAINER VIEWS) проверяют доступ к панели управления для тренеров"""


@pytest.mark.django_db
class TestTrainerViews:
    """Тесты панели управления тренера"""

    def test_trainer_dashboard_accessible(self, client, trainer):
        """
        Проверка: Тренер имеет доступ к своей панели управления
        Ожидание: GET запрос к '/trainers/dashboard/' возвращает HTTP 200
        """
        client.force_login(trainer)
        response = client.get('/trainers/dashboard/')
        assert response.status_code == 200

    def test_trainer_dashboard_blocked_for_regular_user(self, client, user):
        """
        Проверка: Обычный пользователь НЕ имеет доступа к панели тренера
        Ожидание: GET запрос возвращает редирект (302)
        """
        client.force_login(user)
        response = client.get('/trainers/dashboard/')
        # 302 = редирект (нет прав доступа)
        assert response.status_code == 302

    def test_trainer_dashboard_blocked_for_anonymous(self, client):
        """
        Проверка: Анонимный пользователь НЕ имеет доступа к панели тренера
        Ожидание: GET запрос возвращает редирект (302)
        """
        response = client.get('/trainers/dashboard/')
        assert response.status_code == 302

    def test_personal_slots_page(self, client, trainer):
        """
        Проверка: Страница управления персональными слотами доступна тренеру
        Ожидание: GET запрос к '/trainers/personal-slots/' возвращает HTTP 200
        """
        client.force_login(trainer)
        response = client.get('/trainers/personal-slots/')
        assert response.status_code == 200