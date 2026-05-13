import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout, Schedule, Tariff, Booking, TrainerBio
from django.utils import timezone
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

def home(request):
    club_photos = [{'url': '/media/clubs/1.webp', 'title': 'Тренажерный зал'},
                    {'url': '/media/clubs/2.avif', 'title': 'Бассейн'},
                     {'url': '/media/clubs/3.avif', 'title': 'Зона кардио'},]
    context = {'club_photos': club_photos}
    logger.info(f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} открыл главную страницу')
    return render(request, 'home.html', context)


def trainer_list(request):
    bios = TrainerBio.objects.filter(trainer__is_trainer=True).select_related('trainer')
    logger.info(f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} просматривает список тренеров')
    return render(request, 'trainer_list.html', {'bios': bios})


def trainer_detail(request, pk):
    bio = get_object_or_404(TrainerBio, pk=pk)
    logger.info(f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} просматривает профиль тренера: {bio.trainer.full_name}')
    return render(request, 'trainer_detail.html', {'bio': bio})


def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    logger.info(f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} просматривает тренировку: {workout.name}')
    return render(request, 'workout_detail.html', {'workout': workout})


def schedule_list(request):

    selected_difficulty = request.GET.get('difficulty')
    schedules = Schedule.objects.filter(status='active').select_related('workout', 'workout__trainer')

    if selected_difficulty:
        schedules = schedules.filter(workout__difficulty=selected_difficulty)
        logger.info(
            f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} отфильтровал расписание по сложности: {selected_difficulty}')

    today = timezone.now().date()
    now = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_days.append({
            'name': ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'][i],
            'date': day,})

    # Сначала фильтруем по дате недели
    schedules = schedules.filter(date__gte=start_of_week, date__lt=start_of_week + timedelta(days=7))
    schedules = schedules.order_by('date', 'start_time')

    # Затем добавляем статус каждой тренировке
    for schedule in schedules:
        workout_datetime = datetime.combine(schedule.date, schedule.start_time)
        if timezone.is_naive(workout_datetime):
            workout_datetime = timezone.make_aware(workout_datetime)

        workout_end_datetime = workout_datetime + timedelta(minutes=schedule.workout.duration_minutes)

        # Определяем статус тренировки (простая логика)
        if workout_end_datetime < now:
            schedule.status_display = 'completed'  # Завершена (нельзя записаться)
        elif workout_datetime < now:
            schedule.status_display = 'in_progress'  # Идет сейчас (нельзя записаться)
        else:
            schedule.status_display = 'available'  # Доступна (можно записаться)

        # Для отладки - добавим текстовое описание
        if schedule.date < today:
            schedule.debug_date = f"Дата {schedule.date} раньше {today}"
        else:
            schedule.debug_date = f"Дата {schedule.date} не раньше {today}"

        # Для обратной совместимости
        schedule.is_past = workout_datetime < now
        schedule.is_completed = workout_end_datetime < now

    time_slots = list(range(8, 23))

    context = {
        'schedules': schedules,
        'week_days': week_days,
        'time_slots': time_slots,
        'selected_difficulty': selected_difficulty,
        'difficulty_choices': Workout.DIFFICULTY_CHOICES,
        'today': today,
        'now': now,
    }
    return render(request, 'schedule_list.html', context)

def tariff_list(request):
    tariffs = Tariff.objects.all()
    logger.info(f'Пользователь {request.user.full_name if request.user.is_authenticated else "Гость"} просматривает список тарифов')
    return render(request, 'tariff_list.html', {'tariffs': tariffs})


@login_required
def book_workout(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    user_name = request.user.full_name

    logger.info(f'Пользователь {user_name} пытается записаться на тренировку: {schedule.workout.name} ({schedule.date} {schedule.start_time})')
    now = timezone.now()
    workout_datetime = datetime.combine(schedule.date, schedule.start_time)
    if timezone.is_naive(workout_datetime):
        workout_datetime = timezone.make_aware(workout_datetime)

    if workout_datetime < now:
        logger.warning(f'ОТКАЗАНО: Пользователь {user_name} попытался записаться на ПРОШЕДШУЮ тренировку: {schedule.workout.name} ({schedule.date})')
        messages.error(request, 'Нельзя записаться на тренировку, которая уже прошла')
        return redirect('main:schedule_list')

    if schedule.status != 'active':
        logger.warning(f'ОТКАЗАНО: Пользователь {user_name} попытался записаться на НЕАКТИВНУЮ тренировку: {schedule.workout.name}')
        messages.error(request, 'Эта тренировка отменена или уже недоступна')
        return redirect('main:schedule_list')

    if schedule.workout.trainer == request.user:
        logger.warning(f' ОТКАЗАНО: Тренер {user_name} попытался записаться на СВОЮ тренировку: {schedule.workout.name}')
        messages.error(request, 'Вы не можете записаться на собственную тренировку')
        return redirect('main:schedule_list')

    if not request.user.has_active_tariff():
        logger.warning(f' ОТКАЗАНО: Пользователь {user_name} без АКТИВНОГО ТАРИФА пытался записаться на тренировку: {schedule.workout.name}')
        messages.error(request, 'У вас нет активного тарифа. Приобретите тариф для записи на тренировки.')
        return redirect('main:tariff_list')

    workout_time = schedule.start_time
    can_book, error_message = request.user.can_book_workout(workout_time)

    if not can_book:
        logger.warning(f'ОТКАЗАНО: Пользователь {user_name} - {error_message}')
        messages.error(request, error_message)
        return redirect('main:schedule_list')

    if schedule.available_places <= 0:
        logger.warning(f'ОТКАЗАНО: Пользователь {user_name} - нет свободных мест на тренировку: {schedule.workout.name}')
        messages.error(request, 'Нет свободных мест на эту тренировку')
        return redirect('main:schedule_list')

    existing_booking = Booking.objects.filter(user=request.user, schedule=schedule).first()

    if existing_booking and existing_booking.status == 'active':
        logger.warning(f' Пользователь {user_name} уже записан на тренировку: {schedule.workout.name}')
        messages.warning(request, 'Вы уже записаны на эту тренировку')
        return redirect('main:schedule_list')

    if request.method == 'POST':
        if existing_booking and existing_booking.status == 'cancelled':
            existing_booking.status = 'active'
            existing_booking.save()
            schedule.booked_places += 1
            schedule.save()
            logger.info(f'ВОССТАНОВЛЕНА ЗАПИСЬ: Пользователь {user_name} снова записался на тренировку: {schedule.workout.name} ({schedule.date} {schedule.start_time})')
            messages.success(request, f'Вы снова записались на тренировку "{schedule.workout.name}"!')
        else:
            Booking.objects.create(user=request.user, schedule=schedule, status='active')
            schedule.booked_places += 1
            schedule.save()
            logger.info(f' НОВАЯ ЗАПИСЬ: Пользователь {user_name} записался на тренировку: {schedule.workout.name} ({schedule.date} {schedule.start_time})')
            messages.success(request, f'Вы успешно записались на тренировку "{schedule.workout.name}"!')
        logger.info(f' СТАТИСТИКА: На тренировке "{schedule.workout.name}" записано {schedule.booked_places}/{schedule.workout.max_participants} человек')
        return redirect('main:schedule_list')
    return render(request, 'book_workout.html', {'schedule': schedule})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='active')
    user_name = request.user.full_name
    workout_name = booking.schedule.workout.name
    logger.info(f'Пользователь {user_name} пытается отменить запись на тренировку: {workout_name} ({booking.schedule.date} {booking.schedule.start_time})')
    now = timezone.now()
    workout_datetime = datetime.combine(booking.schedule.date, booking.schedule.start_time)
    if timezone.is_naive(workout_datetime):
        workout_datetime = timezone.make_aware(workout_datetime)

    if workout_datetime < now:
        logger.warning(f' ОТКАЗАНО В ОТМЕНЕ: Пользователь {user_name} попытался отменить ПРОШЕДШУЮ тренировку: {workout_name}')
        messages.warning(request, 'Нельзя отменить тренировку, которая уже прошла')
        return redirect('users:profile')

    if booking.schedule.status != 'active':
        logger.warning(f' ОТКАЗАНО В ОТМЕНЕ: Пользователь {user_name} попытался отменить НЕАКТИВНУЮ тренировку: {workout_name}')
        messages.warning(request, 'Эта тренировка уже отменена')
        return redirect('users:profile')

    if request.method == 'POST':
        schedule = booking.schedule
        schedule.booked_places -= 1
        schedule.save()
        booking.status = 'cancelled'
        booking.save()

        logger.info(f'ОТМЕНА ЗАПИСИ: Пользователь {user_name} отменил запись на тренировку: {workout_name} ({booking.schedule.date} {booking.schedule.start_time})')
        logger.info(f'СТАТИСТИКА: На тренировке "{workout_name}" осталось мест: {schedule.available_places}')
        messages.success(request, f'Вы отменили запись на "{workout_name}"')
        return redirect('users:profile')
    return render(request, 'cancel_booking.html', {'booking': booking})