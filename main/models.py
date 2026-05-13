from django.db import models
from datetime import datetime, timedelta, date
from decimal import Decimal

class TrainerBio(models.Model):
    trainer = models.OneToOneField( 'users.User', on_delete=models.CASCADE, primary_key=True,related_name='bio')
    specialty = models.CharField('Специализация', max_length=100)
    experience_years = models.IntegerField('Стаж работы', default=0)
    photo = models.ImageField('Фото', upload_to='trainers/', null=True, blank=True)
    bio = models.TextField('Биография', blank=True)
    achievements = models.TextField('Достижения', blank=True)
    education = models.TextField('Образование', blank=True)

    def __str__(self):
        return f"Биография тренера {self.trainer.full_name}"

    class Meta:
        verbose_name = 'Биография тренера'
        verbose_name_plural = 'Биографии тренеров'


class Workout(models.Model):
    DIFFICULTY_CHOICES = [('beginner', 'Начинающий'),('intermediate', 'Средний'),('advanced', 'Продвинутый'),]
    name = models.CharField('Название', max_length=50, unique=True)
    description = models.TextField('Описание')
    duration_minutes = models.IntegerField('Длительность (мин)')
    difficulty = models.CharField('Сложность', max_length=20 , choices=DIFFICULTY_CHOICES)
    goals = models.CharField('Цели', max_length=100)
    max_participants = models.IntegerField('Макс. участников', default=20)
    trainer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='Тренер', limit_choices_to={'is_trainer': True})
    image = models.ImageField('Изображение', upload_to='workouts/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'


class Schedule(models.Model):
    STATUS_CHOICES = [ ('active', 'Активна'),('cancelled', 'Отменена'),]
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, verbose_name='Тренировка')
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES)
    booked_places = models.IntegerField('Записано человек', default=0)

    @property
    def end_time(self):
        start = datetime.combine(self.date, self.start_time)
        end = start + timedelta(minutes=self.workout.duration_minutes)
        return end.time()

    @property
    def available_places(self):
        return self.workout.max_participants - self.booked_places

    @property
    def is_available(self):
        return self.available_places > 0 and self.status == 'active'

    def __str__(self):
        if self.status == 'cancelled':
            return f"{self.workout.name} - {self.date} - ОТМЕНЕНА"
        return f"{self.workout.name} - {self.date} {self.start_time}"

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'

class Booking(models.Model):
    STATUS_CHOICES = [ ('active', 'Активна'),('cancelled', 'Отменена'),('completed', 'Завершена'), ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings',verbose_name='Пользователь')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='bookings', verbose_name='Расписание')
    booking_date = models.DateTimeField('Дата записи', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.user.username} - {self.schedule.workout.name} - {self.schedule.date}"

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        unique_together = ['user', 'schedule']

class Promotion(models.Model):
    name = models.CharField('Название акции', max_length=100)
    discount_percent = models.IntegerField('Скидка %')
    valid_until = models.DateField('Действует до')
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активна', default=True)

    def is_valid(self):
        return self.is_active and self.valid_until >= date.today()

    def __str__(self):
        return f"{self.name} (-{self.discount_percent}%)"

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

class Tariff(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    duration_days = models.IntegerField('Длительность (дней)')
    has_personal_trainings = models.BooleanField('Доступ к персональным тренировкам', default=False)
    has_unlimited = models.BooleanField('Безлимитное посещение', default=False)
    has_day_time = models.BooleanField('Посещение днем (до 17:00)', default=False)
    has_evening_time = models.BooleanField('Посещение вечером (после 17:00)', default=False)
    has_free_parking = models.BooleanField('Бесплатная парковка', default=False)
    has_personal_locker = models.BooleanField('Собственный шкафчик', default=False)
    has_fitness_testing = models.BooleanField('Анализ состава тела In Body', default=False)
    promotions = models.ManyToManyField('Promotion', verbose_name='Акции', blank=True)

    def get_current_price(self):
        today = date.today()
        active_promotions = self.promotions.filter(is_active=True, valid_until__gte=today)

        if active_promotions.exists():
            max_discount = active_promotions.aggregate(models.Max('discount_percent'))['discount_percent__max']
            discount_decimal = Decimal(max_discount) / Decimal(100)
            return self.price * (Decimal(1) - discount_decimal)
        return self.price

    def get_discount_percent(self):
        today = date.today()
        active_promotions = self.promotions.filter(is_active=True, valid_until__gte=today)

        if active_promotions.exists():
            return active_promotions.aggregate(models.Max('discount_percent'))['discount_percent__max']
        return 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

