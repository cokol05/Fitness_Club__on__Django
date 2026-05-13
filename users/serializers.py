from rest_framework import serializers
from django.contrib.auth import get_user_model
from main.models import Booking
from main.serializers import ScheduleSerializer
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    has_active_tariff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'phone', 'birth_date','is_trainer', 'tariff_name', 'tariff_price','tariff_end_date', 'tariff_type', 'has_active_tariff')
        read_only_fields = ('id', 'is_trainer', 'tariff_price')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'birth_date', 'password', 'password_confirm')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserBookingSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    workout_name = serializers.CharField(source='schedule.workout.name', read_only=True)
    workout_date = serializers.DateField(source='schedule.date', read_only=True)
    workout_time = serializers.TimeField(source='schedule.start_time', read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'schedule', 'workout_name', 'workout_date',
                  'workout_time', 'status', 'booking_date')