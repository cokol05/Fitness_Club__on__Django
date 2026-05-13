import pytest
from datetime import date, time, timedelta
from decimal import Decimal

""""(USER MODEL) проверяют создание пользователей, роли и методы"""

@pytest.mark.django_db
class TestUserModel:
    """Тесты модели пользователя"""

    def test_create_user(self, user):
        """
        Проверка: Обычный пользователь создаётся корректно
        Ожидание: Поля email, full_name заполнены, is_trainer = False
        """
        assert user.email == 'user@test.com'
        assert user.full_name == 'Test User'
        assert not user.is_trainer  # Обычный пользователь не тренер

    def test_create_trainer(self, trainer):
        """
        Проверка: Тренер создаётся корректно
        Ожидание: Поле is_trainer = True
        """
        assert trainer.is_trainer  # Тренер имеет специальный статус

    def test_str_method(self, user):
        """
        Проверка: Метод __str__ возвращает ФИО пользователя
        Ожидание: str(user) == 'Test User'
        """
        assert str(user) == 'Test User'

    def test_has_active_tariff_true(self, user_with_tariff):
        """
        Проверка: has_active_tariff() возвращает True, если тариф активен
        Ожидание: Пользователь с тарифом имеет активный тариф
        """
        assert user_with_tariff.has_active_tariff() is True

    def test_has_active_tariff_false(self, user):
        """
        Проверка: has_active_tariff() возвращает False, если тарифа нет
        Ожидание: Пользователь без тарифа не имеет активного тарифа
        """
        assert user.has_active_tariff() is False

    def test_can_book_workout(self, user_with_tariff):
        """
        Проверка: can_book_workout() определяет возможность записи
        Ожидание: В 15:00 (до 17:00) можно записаться
        """
        from datetime import time
        can_book, _ = user_with_tariff.can_book_workout(time(15, 0))
        assert can_book is True


"""(WORKOUT MODEL) проверяют создание тренировок и связи"""

@pytest.mark.django_db
class TestWorkoutModel:
    """Тесты модели тренировки"""

    def test_create_workout(self, workout):
        """
        Проверка: Тренировка создаётся корректно
        Ожидание: Поля name и duration_minutes заполнены верно
        """
        assert workout.name == 'Test Workout'
        assert workout.duration_minutes == 60

    def test_str_method(self, workout):
        """
        Проверка: Метод __str__ возвращает название тренировки
        Ожидание: str(workout) == 'Test Workout'
        """
        assert str(workout) == 'Test Workout'

    def test_trainer_relation(self, workout, trainer):
        """
        Проверка: Связь тренировки с тренером работает
        Ожидание: У тренировки есть тренер
        """
        assert workout.trainer == trainer


"""(SCHEDULE MODEL) проверяют создание расписания и вычисляемые поля"""

@pytest.mark.django_db
class TestScheduleModel:
    """Тесты модели расписания"""

    def test_create_schedule(self, schedule):
        """
        Проверка: Расписание создаётся корректно
        Ожидание: Статус активен, свободных мест = 10
        """
        assert schedule.status == 'active'
        assert schedule.available_places == 10

    def test_end_time_property(self, workout):
        """
        Проверка: Свойство end_time вычисляет время окончания
        Ожидание: При start_time 10:00 и длительности 60 мин → окончание 11:00
        """
        from main.models import Schedule
        sched = Schedule.objects.create(
            workout=workout,
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            status='active'
        )
        assert sched.end_time == time(11, 0)  # 10:00 + 60 мин = 11:00

    def test_available_places_property(self, schedule):
        """
        Проверка: available_places вычисляет количество свободных мест
        Ожидание: Макс. участников (20) - записано (10) = 10 свободно
        """
        assert schedule.available_places == 10  # 20 - 10 = 10

    def test_is_available_true(self, schedule):
        """
        Проверка: is_available = True, если есть места и тренировка активна
        Ожидание: При свободных местах и статусе 'active' → True
        """
        assert schedule.is_available is True

    def test_is_available_false_cancelled(self, workout):
        """
        Проверка: is_available = False, если тренировка отменена
        Ожидание: При статусе 'cancelled' → False, даже если места есть
        """
        from main.models import Schedule
        sched = Schedule.objects.create(
            workout=workout,
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            status='cancelled'  # Отменена
        )
        assert sched.is_available is False  # Отменена → недоступна


""""(TARIFF MODEL) проверяют создание тарифов и расчёт цены со скидкой"""

@pytest.mark.django_db
class TestTariffModel:
    """Тесты модели тарифа"""

    def test_create_tariff(self, tariff):
        """
        Проверка: Тариф создаётся корректно
        Ожидание: Поля name и price заполнены верно
        """
        assert tariff.name == 'Monthly'
        assert tariff.price == Decimal('5000.00')

    def test_str_method(self, tariff):
        """
        Проверка: Метод __str__ возвращает название тарифа
        Ожидание: str(tariff) == 'Monthly'
        """
        assert str(tariff) == 'Monthly'

    def test_get_current_price(self, tariff):
        """
        Проверка: get_current_price() возвращает цену без скидки
        Ожидание: Если нет активных акций, цена не меняется
        """
        assert tariff.get_current_price() == Decimal('5000.00')


""""(TRAINERBIO MODEL) проверяют связь с пользователем и правильность данных"""

@pytest.mark.django_db
class TestTrainerBioModel:
    """Тесты биографии тренера"""

    def test_create_trainer_bio(self, trainer_bio, trainer):
        """
        Проверка: Биография тренера создаётся корректно
        Ожидание: Связана с тренером, специализация указана
        """
        assert trainer_bio.trainer == trainer
        assert trainer_bio.specialty == 'Yoga Instructor'

    def test_str_method(self, trainer_bio, trainer):
        """
        Проверка: Метод __str__ содержит имя тренера
        Ожидание: В строковом представлении есть ФИО тренера
        """
        assert trainer.full_name in str(trainer_bio)