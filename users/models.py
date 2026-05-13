from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class User(AbstractUser):
    first_name = None
    last_name = None
    username = None

    full_name = models.CharField('ФИО', max_length=200)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=12, blank=True, unique=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    is_trainer = models.BooleanField('Тренер', default=False)

    tariff_name = models.CharField('Название тарифа', max_length=100, blank=True, null=True)
    tariff_price = models.DecimalField('Цена тарифа', max_digits=10, decimal_places=2, blank=True, null=True)
    tariff_duration = models.IntegerField('Длительность тарифа (дней)', blank=True, null=True)
    tariff_purchase_date = models.DateField('Дата покупки', auto_now_add=True, null=True)
    tariff_end_date = models.DateField('Дата окончания тарифа', blank=True, null=True)
    tariff_type = models.CharField(  'Тип тарифа',max_length=20,choices=[('day', 'Дневной (до 17:00)'), ('evening', 'Вечерний (после 17:00)'), ('unlimited', 'Безлимитный')],blank=True,null=True)
    tariff_has_personal = models.BooleanField('Доступ к персональным тренировкам', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def has_active_tariff(self):
        if self.tariff_end_date:
            return self.tariff_end_date >= date.today()
        return False

    def has_personal_trainings_access(self):
        return self.has_active_tariff() and self.tariff_has_personal

    def can_book_workout(self, workout_time):
        if not self.has_active_tariff():
            return False, 'У вас нет активного тарифа. Приобретите тариф для записи на тренировки.'
        hour = workout_time.hour
        if self.tariff_type == 'day' and hour >= 17:
            return False, 'Ваш дневной тариф действует только до 17:00.'
        if self.tariff_type == 'evening' and hour < 17:
            return False, 'Ваш вечерний тариф действует только после 17:00.'
        return True, 'OK'

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
