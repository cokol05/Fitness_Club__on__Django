from django.urls import path
from . import views
from . import views_api

app_name = 'trainers'

urlpatterns = [
    path('dashboard/', views.trainer_dashboard, name='dashboard'),
    path('personal-slots/', views.personal_training_slots, name='personal_slots'),
    path('personal-slots/create/', views.create_personal_slot, name='create_slot'),
    path('personal/<int:pt_id>/cancel/', views.cancel_personal_training, name='cancel_personal'),

    path('api/v1/', views_api.api_root, name='api_root'),
    path('api/v1/my-slots/', views_api.trainer_slots, name='api_my_slots'),
    path('api/v1/slots/create/', views_api.trainer_slots, name='api_create_slot'),
    path('api/v1/slots/<int:slot_id>/delete/', views_api.delete_slot, name='api_delete_slot'),
    path('api/v1/trainers/<int:trainer_id>/slots/', views_api.available_slots, name='api_available_slots'),
    path('api/v1/slots/<int:slot_id>/book/', views_api.book_slot, name='api_book_slot'),]