from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Workout, Schedule, Tariff, TrainerBio, Booking
from .serializers import (WorkoutSerializer, ScheduleSerializer, TariffSerializer,TrainerBioSerializer, UserSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET', 'POST'])
def api_root(request):
    if request.method == 'GET':
        return Response({
            'message': 'Добро пожаловать в Fitness Club API!',
            'endpoints': {
                'workouts': '/api/v1/workouts/',
                'schedules': '/api/v1/schedules/',
                'tariffs': '/api/v1/tariffs/',
                'trainers': '/api/v1/trainers/',
                'profile': '/api/v1/users/<id>/',
                'book': '/api/v1/book/' }})
    return Response({'message': 'Получены данные', 'data': request.data})

@api_view(['GET', 'POST'])
def workout_list(request):
    if request.method == 'GET':
        workouts = Workout.objects.all()
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WorkoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    if request.method == 'GET':
        serializer = WorkoutSerializer(workout)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WorkoutSerializer(workout, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = WorkoutSerializer(workout, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        workout.delete()
        return Response({"message": "Тренировка удалена"}, status=status.HTTP_204_NO_CONTENT)
    return None

@api_view(['GET'])
def schedule_list(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    schedules = Schedule.objects.filter(status='active',date__gte=start_of_week,date__lt=end_of_week).select_related('workout', 'workout__trainer')
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    serializer = ScheduleSerializer(schedule)
    return Response(serializer.data)

@api_view(['GET'])
def tariff_list(request):
    tariffs = Tariff.objects.all()
    serializer = TariffSerializer(tariffs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tariff_detail(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)
    serializer = TariffSerializer(tariff)
    return Response(serializer.data)

@api_view(['GET'])
def trainer_list(request):
    bios = TrainerBio.objects.select_related('trainer').all()
    serializer = TrainerBioSerializer(bios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def trainer_detail(request, pk):
    bio = get_object_or_404(TrainerBio, pk=pk)
    serializer = TrainerBioSerializer(bio)
    return Response(serializer.data)

@api_view(['GET', 'PATCH'])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.user != user and not request.user.is_staff:
        return Response({"error": "У вас нет прав для просмотра этого профиля"},status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None


@api_view(['POST'])
def book_workout_api(request):
    schedule_id = request.data.get('schedule_id')

    if not request.user.is_authenticated:
        return Response( {"error": "Необходима авторизация"},status=status.HTTP_401_UNAUTHORIZED)

    if not schedule_id:
        return Response({"error": "Поле schedule_id обязательно"},status=status.HTTP_400_BAD_REQUEST)

    schedule = get_object_or_404(Schedule, id=schedule_id)
    errors = {}
    now = timezone.now()
    workout_datetime = datetime.combine(schedule.date, schedule.start_time)
    if timezone.is_naive(workout_datetime):
        workout_datetime = timezone.make_aware(workout_datetime)

    if workout_datetime < now:
        errors['date'] = 'Нельзя записаться на прошедшую тренировку'
    if schedule.status != 'active':
        errors['status'] = 'Эта тренировка отменена или уже недоступна'
    if schedule.workout.trainer == request.user:
        errors['trainer'] = 'Вы не можете записаться на собственную тренировку'
    if not request.user.has_active_tariff():
        errors['tariff'] = 'У вас нет активного тарифа'
    if request.user.has_active_tariff():
        can_book, error_message = request.user.can_book_workout(schedule.start_time)
        if not can_book:
            errors['tariff_time'] = error_message

    if schedule.available_places <= 0:
        errors['places'] = 'Нет свободных мест'

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    existing_booking = Booking.objects.filter(user=request.user, schedule=schedule).first()

    if existing_booking and existing_booking.status == 'active':
        return Response({"error": "Вы уже записаны на эту тренировку"},status=status.HTTP_400_BAD_REQUEST)

    if existing_booking and existing_booking.status == 'cancelled':
        existing_booking.status = 'active'
        existing_booking.save()
        schedule.booked_places += 1
        schedule.save()
        return Response({
            "message": f"Вы снова записались на тренировку '{schedule.workout.name}'!",
            "booking_id": existing_booking.id,
            "schedule_id": schedule.id,
            "workout_name": schedule.workout.name,
            "date": schedule.date,
            "time": schedule.start_time}, status=status.HTTP_200_OK)
    else:
        booking = Booking.objects.create(user=request.user,schedule=schedule,status='active')
        schedule.booked_places += 1
        schedule.save()
        return Response({
            "message": f"Вы успешно записались на тренировку '{schedule.workout.name}'!",
            "booking_id": booking.id,
            "schedule_id": schedule.id,
            "workout_name": schedule.workout.name,
            "date": schedule.date,
            "time": schedule.start_time}, status=status.HTTP_201_CREATED)