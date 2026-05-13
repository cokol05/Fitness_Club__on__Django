from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class PersonalTraining(models.Model):
    STATUS_CHOICES = [('available', 'Доступна'),('booked', 'Забронирована'),]
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personal_trainings', limit_choices_to={'is_trainer': True}, verbose_name='Тренер')
    client = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_trainings_as_client')
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    status = models.CharField('Статус', max_length=30, choices=STATUS_CHOICES, default='available')

    @property
    def is_available(self):
        return self.status == 'available' and self.client is None

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Время окончания должно быть позже времени начала')

        from datetime import date
        if self.date < date.today():
            raise ValidationError('Дата тренировки не может быть в прошлом')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trainer.full_name} - {self.date} {self.start_time}"

    class Meta:
        verbose_name = 'Персональная тренировка'
        verbose_name_plural = 'Персональные тренировки'