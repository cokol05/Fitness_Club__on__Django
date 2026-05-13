from django.contrib import admin
from .models import TrainerBio, Workout, Schedule, Tariff, Promotion


@admin.register(TrainerBio)
class TrainerBioAdmin(admin.ModelAdmin):
    list_display = ('get_trainer_name', 'specialty', 'experience_years')

    def get_trainer_name(self, obj):
        return obj.trainer.full_name if obj.trainer else '-'
    get_trainer_name.short_description = 'Тренер'


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'duration_minutes', 'max_participants', 'get_trainer_name')

    def get_trainer_name(self, obj):
        return obj.trainer.full_name if obj.trainer else '-'
    get_trainer_name.short_description = 'Тренер'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('workout', 'date', 'start_time', 'get_end_time', 'available_places')
    exclude = ('booked_places',)

    def get_end_time(self, obj):
        return obj.end_time
    get_end_time.short_description = 'Время окончания'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'valid_until', 'is_active')


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'get_current_price_display', 'duration_days')


    def get_current_price_display(self, obj):
        discount = obj.get_discount_percent()
        if discount > 0:
            return f"{obj.price} → {obj.get_current_price()} ₽ (-{discount}%)"
        return f"{obj.price} ₽"
    get_current_price_display.short_description = 'Цена со скидкой'
