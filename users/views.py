import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, date
from .forms import CustomUserCreationForm
from .models import User
from main.models import Tariff, Booking, Schedule, TrainerBio
from trainers.models import PersonalTraining
from django.utils import timezone
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'НОВЫЙ ПОЛЬЗОВАТЕЛЬ: {user.full_name} ({user.email}) зарегистрировался')
            messages.success(request, 'Регистрация успешна!')
            return redirect('main:home')
        else:
            logger.warning(f' ОШИБКА РЕГИСТРАЦИИ: {form.errors}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            logger.info(f'ВХОД: {user.full_name} ({email}) вошёл в систему')
            return redirect('main:home')
        else:
            logger.warning(f' НЕУДАЧНЫЙ ВХОД: попытка входа с email {email}')
            messages.error(request, 'Неверный email или пароль')
    return render(request, 'login.html')


def logout_view(request):
    user_name = request.user.full_name if request.user.is_authenticated else "Гость"
    logger.info(f' ВЫХОД: {user_name} вышел из системы')
    logout(request)
    return redirect('main:home')

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user, status='active')
    tariff_active = request.user.has_active_tariff()
    logger.info(f'ПРОФИЛЬ: {request.user.full_name} просматривает свой профиль')

    context = {
        'user': request.user,
        'bookings': bookings,
        'tariff_active': tariff_active,
        'now': timezone.now().date(),}
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.birth_date = request.POST.get('birth_date')
        user.save()

        logger.info(f'ПРОФИЛЬ ОБНОВЛЁН: {user.full_name} обновил свои данные')
        messages.success(request, 'Профиль обновлён')
        return redirect('users:profile')
    return render(request, 'edit_profile.html')

@login_required
def buy_tariff(request, tariff_id):
    tariff = get_object_or_404(Tariff, id=tariff_id)
    user_name = request.user.full_name

    if request.method == 'POST':
        request.user.tariff_name = tariff.name
        request.user.tariff_price = tariff.get_current_price()
        request.user.tariff_duration = tariff.duration_days
        request.user.tariff_purchase_date = date.today()
        request.user.tariff_end_date = date.today() + timedelta(days=tariff.duration_days)

        if tariff.has_day_time and not tariff.has_evening_time:
            request.user.tariff_type = 'day'
        elif tariff.has_evening_time and not tariff.has_day_time:
            request.user.tariff_type = 'evening'
        else:
            request.user.tariff_type = 'unlimited'

        request.user.tariff_has_personal = tariff.has_personal_trainings
        request.user.save()

        discount = tariff.get_discount_percent()
        if discount > 0:
            logger.info(f'ПОКУПКА ТАРИФА: {user_name} купил тариф "{tariff.name}" со скидкой {discount}% за {tariff.get_current_price()} ₽')
            messages.success(request, f'Тариф "{tariff.name}" приобретён со скидкой {discount}%!')
        else:
            logger.info(f' ПОКУПКА ТАРИФА: {user_name} купил тариф "{tariff.name}" за {tariff.get_current_price()} ₽')
            messages.success(request, f'Тариф "{tariff.name}" успешно приобретён!')
        return redirect('users:profile')
    return render(request, 'buy_tariff.html', {'tariff': tariff})

@login_required
def personal_trainers(request):
    trainers = TrainerBio.objects.filter(trainer__is_trainer=True)
    logger.info(f'ПЕРСОНАЛЬНЫЕ ТРЕНЕРЫ: {request.user.full_name} просматривает список тренеров')
    return render(request, 'personal_trainers.html', {'trainers': trainers})


@login_required
def trainer_slots(request, trainer_id):
    trainer = get_object_or_404(User, id=trainer_id, is_trainer=True)
    slots = PersonalTraining.objects.filter(trainer=trainer, status='available', date__gte=date.today())
    logger.info(f' СЛОТЫ ТРЕНЕРА: {request.user.full_name} просматривает слоты тренера {trainer.full_name}')
    return render(request, 'trainer_slots.html', {'trainer': trainer, 'slots': slots})

@login_required
def book_personal(request, slot_id):
    slot = get_object_or_404(PersonalTraining, id=slot_id, status='available')
    user_name = request.user.full_name

    if slot.trainer == request.user:
        logger.warning(f'ОТКАЗАНО: {user_name} попытался записаться к себе')
        messages.error(request, 'Нельзя записаться к себе')
        return redirect('users:personal_trainers')

    if request.method == 'POST':
        slot.client = request.user
        slot.status = 'booked'
        slot.save()

        logger.info(f' ЗАПИСЬ НА ПЕРСОНАЛЬНУЮ ТРЕНИРОВКУ: {user_name} записался к тренеру {slot.trainer.full_name} на {slot.date} {slot.start_time}')
        messages.success(request, f'Вы записались на {slot.date}')
        return redirect('users:profile')
    return render(request, 'book_personal.html', {'slot': slot})

@login_required
def cancel_personal(request, slot_id):
    slot = get_object_or_404(PersonalTraining, id=slot_id, client=request.user, status='booked')
    user_name = request.user.full_name
    trainer_name = slot.trainer.full_name

    if request.method == 'POST':
        logger.info( f'ОТМЕНА ПЕРСОНАЛЬНОЙ ТРЕНИРОВКИ: {user_name} отменил запись к тренеру {trainer_name} на {slot.date} {slot.start_time}')

        slot.client = None
        slot.status = 'available'
        slot.save()

        messages.success(request, 'Запись отменена')
        return redirect('users:profile')
    return render(request, 'cancel_personal_booking.html', {'slot': slot})

@login_required
def password_change(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')

        if not request.user.check_password(old):
            messages.error(request, 'Неверный старый пароль')
        elif new1 != new2:
            messages.error(request, 'Пароли не совпадают')
        elif len(new1) < 8:
            messages.error(request, 'Пароль слишком короткий')
        else:
            request.user.set_password(new1)
            request.user.save()
            login(request, request.user)
            logger.info(f' СМЕНА ПАРOЛЯ: {request.user.full_name} сменил пароль')
            messages.success(request, 'Пароль изменён')
            return redirect('users:profile')
    return render(request, 'password_change_form.html')


def password_change_done(request):
    return render(request, 'password_change_done.html')

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            logger.info(f' ВОССТАНОВЛЕНИЕ ПАРОЛЯ: Запрошен сброс пароля для {email}')
            messages.success(request, 'Ссылка для сброса пароля отправлена')
            return redirect('users:password_reset_done')
        except User.DoesNotExist:
            logger.warning(f' ОШИБКА: Попытка сброса пароля для несуществующего email {email}')
            messages.error(request, 'Пользователь не найден')
    return render(request, 'password_reset_form.html')


def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')
        if new1 == new2:
            logger.info(f' ПАРОЛЬ СБРОШЕН: Пользователь успешно сбросил пароль')
            messages.success(request, 'Пароль изменён')
            return redirect('users:login')
        else:
            messages.error(request, 'Пароли не совпадают')
    return render(request, 'password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')
