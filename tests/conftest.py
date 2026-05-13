import pytest
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from decimal import Decimal
User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create(
        email='user@test.com',
        full_name='Test User',
        phone='+79991234567',
        birth_date=date(1990, 1, 1),
        is_trainer=False)

@pytest.fixture
def trainer(db):
    return User.objects.create(
        email='trainer@test.com',
        full_name='Test Trainer',
        phone='+79991234568',
        birth_date=date(1985, 1, 1),
        is_trainer=True)

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@test.com',
        full_name='Admin',
        phone='+79991234569',
        birth_date=date(1980, 1, 1),
        password='admin123')

@pytest.fixture
def user_with_tariff(user):
    user.tariff_end_date = date.today() + timedelta(days=30)
    user.tariff_type = 'unlimited'
    user.tariff_has_personal = True
    user.save()
    return user

@pytest.fixture
def workout(trainer):
    from main.models import Workout
    return Workout.objects.create(
        name='Test Workout',
        description='Test description',
        duration_minutes=60,
        difficulty='beginner',
        goals='Fitness',
        max_participants=10,
        trainer=trainer)

@pytest.fixture
def schedule(workout):
    from main.models import Schedule
    return Schedule.objects.create(
        workout=workout,
        date=date.today() + timedelta(days=1),
        start_time=time(10, 0),
        status='active',
        booked_places=0)

@pytest.fixture
def past_schedule(workout):
    from main.models import Schedule
    return Schedule.objects.create(
        workout=workout,
        date=date.today() - timedelta(days=1),
        start_time=time(10, 0),
        status='active',
        booked_places=0)

@pytest.fixture
def full_schedule(workout):
    from main.models import Schedule
    return Schedule.objects.create(
        workout=workout,
        date=date.today() + timedelta(days=1),
        start_time=time(10, 0),
        status='active',
        booked_places=workout.max_participants)

@pytest.fixture
def tariff(db):
    from main.models import Tariff
    return Tariff.objects.create(
        name='Monthly',
        price=Decimal('5000.00'),
        duration_days=30,
        has_unlimited=True)

@pytest.fixture
def trainer_bio(trainer):
    from main.models import TrainerBio
    return TrainerBio.objects.create(
        trainer=trainer,
        specialty='Yoga Instructor',
        experience_years=10,
        bio='Experienced teacher' )

@pytest.fixture
def personal_slot(trainer):
    from trainers.models import PersonalTraining
    return PersonalTraining.objects.create(
        trainer=trainer,
        date=date.today() + timedelta(days=5),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status='available')