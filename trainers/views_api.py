from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import PersonalTraining
from .serializers import PersonalTrainingSerializer, PersonalTrainingCreateSerializer
User = get_user_model()

def is_trainer(user):
    return user.is_authenticated and user.is_trainer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request):
    return Response({
        'message': 'Fitness Club API - Тренеры',
        'endpoints': {
            'my_slots': '/api/v1/trainers/my-slots/',
            'create_slot': '/api/v1/trainers/slots/create/',}})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def trainer_slots(request):

    # Проверка, что пользователь - тренер
    if not request.user.is_trainer:
        return Response(
            {"error": "Только тренеры могут управлять слотами"},
            status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        slots = PersonalTraining.objects.filter(trainer=request.user).order_by('date', 'start_time')
        serializer = PersonalTrainingSerializer(slots, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PersonalTrainingCreateSerializer(data=request.data)
        if serializer.is_valid():
            slot = PersonalTraining.objects.create(
                trainer=request.user,
                date=serializer.validated_data['date'],
                start_time=serializer.validated_data['start_time'],
                end_time=serializer.validated_data['end_time'],
                status='available'
            )
            return Response(
                PersonalTrainingSerializer(slot).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_slot(request, slot_id):
    slot = get_object_or_404(PersonalTraining, id=slot_id)

    # Проверка, что пользователь - владелец слота
    if slot.trainer != request.user:
        return Response(
            {"error": "Вы можете удалять только свои слоты"},
            status=status.HTTP_403_FORBIDDEN)

    slot.delete()
    return Response(
        {"message": "Слот успешно удалён"},
        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_slots(request, trainer_id):
    trainer = get_object_or_404(User, id=trainer_id, is_trainer=True)

    from datetime import date
    slots = PersonalTraining.objects.filter(
        trainer=trainer,
        status='available',
        client__isnull=True,
        date__gte=date.today() ).order_by('date', 'start_time')
    serializer = PersonalTrainingSerializer(slots, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_slot(request, slot_id):
    slot = get_object_or_404(PersonalTraining, id=slot_id, status='available')

    # Проверка, что пользователь не тренер
    if request.user.is_trainer:
        return Response(
            {"error": "Тренеры не могут записываться на персональные тренировки как клиенты"},
            status=status.HTTP_403_FORBIDDEN)

    # Проверка, что пользователь не записывается к себе
    if slot.trainer == request.user:
        return Response(
            {"error": "Нельзя записаться на тренировку к себе"},
            status=status.HTTP_400_BAD_REQUEST)

    # Проверка, есть ли у пользователя доступ к персональным тренировкам по тарифу
    if not request.user.tariff_has_personal:
        return Response(
            {"error": "Ваш тариф не включает персональные тренировки"},
            status=status.HTTP_400_BAD_REQUEST)

    slot.client = request.user
    slot.status = 'booked'
    slot.save()

    return Response(
        {"message": f"Вы записались на персональную тренировку к {slot.trainer.full_name} на {slot.date}"},
        status=status.HTTP_200_OK)