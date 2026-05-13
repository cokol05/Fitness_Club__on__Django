import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import datetime
from main.models import Schedule
from .models import PersonalTraining
logger = logging.getLogger(__name__)


def is_trainer(user):
    return user.is_authenticated and user.is_trainer


@login_required
@user_passes_test(is_trainer)
def trainer_dashboard(request):
    trainer_name = request.user.full_name
    schedules = Schedule.objects.filter(
        workout__trainer=request.user,
        status='active',
        date__gte=datetime.now().date()).order_by('date', 'start_time')

    personal_trainings = PersonalTraining.objects.filter(
        trainer=request.user,
        date__gte=datetime.now().date()).order_by('date', 'start_time')

    logger.info(f' ПАНЕЛЬ ТРЕНЕРА: {trainer_name} открыл панель управления. Групповых: {schedules.count()}, Персональных: {personal_trainings.count()}')

    context = {
        'schedules': schedules,
        'personal_trainings': personal_trainings,
        'user': request.user,}
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(is_trainer)
def personal_training_slots(request):
    slots = PersonalTraining.objects.filter(trainer=request.user).order_by('date', 'start_time')
    logger.info(f' СПИСОК СЛОТОВ: Тренер {request.user.full_name} просматривает свои слоты. Всего: {slots.count()}')
    return render(request, 'personal_slots.html', {'slots': slots})


@login_required
@user_passes_test(is_trainer)
def create_personal_slot(request):
    trainer_name = request.user.full_name

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            slot = PersonalTraining.objects.create(
                trainer=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time)
            logger.info(f' СОЗДАН СЛОТ: Тренер {trainer_name} создал слот на {date} {start_time}-{end_time}')
            messages.success(request, 'Слот для персональной тренировки создан')
        except Exception as e:
            logger.error(f' ОШИБКА: Тренер {trainer_name} не смог создать слот - {str(e)}')
            messages.error(request, f'Ошибка: {str(e)}')

        return redirect('trainers:personal_slots')

    return render(request, 'create_slot.html')


@login_required
@user_passes_test(is_trainer)
def cancel_personal_training(request, pt_id):
    pt = get_object_or_404(PersonalTraining, id=pt_id, trainer=request.user)
    trainer_name = request.user.full_name

    if request.method == 'POST':
        client_name = pt.client.full_name if pt.client else None
        date_str = pt.date.strftime('%d.%m.%Y')

        pt.delete()

        if client_name:
            logger.info(f' УДАЛЕНИЕ ЗАПИСИ: Тренер {trainer_name} удалил запись клиента {client_name} на {date_str}')
            messages.success(request, f'Запись клиента {client_name} на {date_str} удалена')
        else:
            logger.info(f' УДАЛЕНИЕ СЛОТА: Тренер {trainer_name} удалил свободный слот на {date_str}')
            messages.success(request, f'Слот на {date_str} удален')

        return redirect('trainers:personal_slots')

    return render(request, 'cancel_personal.html', {'pt': pt})