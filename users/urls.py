from django.urls import path
from . import views
from . import views_api

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('tariff/<int:tariff_id>/buy/', views.buy_tariff, name='buy_tariff'),
    path('personal-trainers/', views.personal_trainers, name='personal_trainers'),
    path('trainer/<int:trainer_id>/slots/', views.trainer_slots, name='trainer_slots'),
    path('book-personal/<int:slot_id>/', views.book_personal, name='book_personal'),
    path('cancel-personal/<int:slot_id>/', views.cancel_personal, name='cancel_personal'),
    path('password-change/', views.password_change, name='password_change'),
    path('password-change/done/', views.password_change_done, name='password_change_done'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),

    path('api/v1/', views_api.api_root, name='api_root'),
    path('api/v1/me/', views_api.current_user, name='api_current_user'),
    path('api/v1/users/<int:pk>/', views_api.user_detail, name='api_user_detail'),
    path('api/v1/register/', views_api.register, name='api_register'),
    path('api/v1/login/', views_api.login_api, name='api_login'),
    path('api/v1/my-bookings/', views_api.my_bookings, name='api_my_bookings'),
    path('api/v1/bookings/<int:booking_id>/cancel/', views_api.cancel_booking_api, name='api_cancel_booking'),
]