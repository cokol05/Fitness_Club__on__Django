from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer, UserBookingSerializer
from main.models import Booking
User = get_user_model()


@api_view(['GET'])
def api_root(request):
    """Корневой эндпоинт API пользователей"""
    return Response({
        'message': 'Fitness Club API - Пользователи',
        'endpoints': {
            'me': '/api/v1/users/me/',
            'login': '/api/v1/users/login/',
            'register': '/api/v1/users/register/',
            'my_bookings': '/api/v1/users/my-bookings/',}})

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Проверка прав: только админ или сам пользователь
    if request.user != user and not request.user.is_staff:
        return Response(
            {"error": "У вас нет прав для просмотра этого профиля"},
            status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "Пользователь успешно зарегистрирован", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"error": "Email и пароль обязательны"},
            status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if user is not None:
        # Для API не используем сессии, просто возвращаем данные пользователя
        return Response({
            "message": "Успешный вход",
            "user": UserSerializer(user).data})
    else:
        return Response(
            {"error": "Неверный email или пароль"},
            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user,
        status='active'
    ).select_related('schedule', 'schedule__workout')

    serializer = UserBookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking_api(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='active')
    schedule = booking.schedule
    schedule.booked_places -= 1
    schedule.save()

    booking.status = 'cancelled'
    booking.save()
    return Response(
        {"message": f"Запись на '{schedule.workout.name}' отменена"},
        status=status.HTTP_200_OK)