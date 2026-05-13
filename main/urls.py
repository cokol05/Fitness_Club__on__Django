from django.urls import path
from . import views
from . import views_api

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('trainers/<int:pk>/', views.trainer_detail, name='trainer_detail'),
    path('workouts/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('schedule/', views.schedule_list, name='schedule_list'),
    path('schedule/<int:schedule_id>/book/', views.book_workout, name='book_workout'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('tariffs/', views.tariff_list, name='tariff_list'),

    path('api/v1/', views_api.api_root, name='api_root'),
    path('api/v1/workouts/', views_api.workout_list, name='api_workout_list'),
    path('api/v1/workouts/<int:pk>/', views_api.workout_detail, name='api_workout_detail'),
    path('api/v1/schedules/', views_api.schedule_list, name='api_schedule_list'),
    path('api/v1/schedules/<int:pk>/', views_api.schedule_detail, name='api_schedule_detail'),
    path('api/v1/tariffs/', views_api.tariff_list, name='api_tariff_list'),
    path('api/v1/tariffs/<int:pk>/', views_api.tariff_detail, name='api_tariff_detail'),
    path('api/v1/trainers/', views_api.trainer_list, name='api_trainer_list'),
    path('api/v1/trainers/<int:pk>/', views_api.trainer_detail, name='api_trainer_detail'),
    path('api/v1/users/<int:pk>/', views_api.user_detail, name='api_user_detail'),
    path('api/v1/book/', views_api.book_workout_api, name='api_book_workout'),]