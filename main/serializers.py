# main/serializers.py
from rest_framework import serializers
from .models import Workout, Schedule, Tariff, TrainerBio
from users.models import User


class TrainerBioSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='trainer.id', read_only=True)
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    trainer_email = serializers.EmailField(source='trainer.email', read_only=True)

    class Meta:
        model = TrainerBio
        fields = ['id', 'trainer', 'trainer_name', 'trainer_email', 'specialty',
                  'experience_years', 'photo', 'bio', 'achievements', 'education']
        read_only_fields = ['trainer']


class WorkoutSerializer(serializers.ModelSerializer):
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)

    class Meta:
        model = Workout
        fields = ('id', 'name', 'description', 'duration_minutes', 'difficulty',
                  'difficulty_display', 'goals', 'max_participants', 'trainer',
                  'trainer_name', 'image')


class ScheduleSerializer(serializers.ModelSerializer):
    workout_name = serializers.CharField(source='workout.name', read_only=True)
    trainer_name = serializers.CharField(source='workout.trainer.full_name', read_only=True)
    available_places = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'workout', 'workout_name', 'trainer_name', 'date',
                  'start_time', 'end_time', 'status', 'booked_places',
                  'available_places', 'is_available')


class TariffSerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tariff
        fields = ('id', 'name', 'price', 'current_price', 'discount_percent',
                  'duration_days', 'has_personal_trainings', 'has_unlimited',
                  'has_day_time', 'has_evening_time', 'has_free_parking',
                  'has_personal_locker', 'has_fitness_testing')


class UserSerializer(serializers.ModelSerializer):
    has_active_tariff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'phone', 'birth_date',
                  'is_trainer', 'tariff_name', 'tariff_end_date',
                  'has_active_tariff')