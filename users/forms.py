from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from datetime import date
from .models import User


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО',max_length=200,required=True,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Иванов Иван Иванович'}))
    email = forms.EmailField(label='Email',required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'}))
    phone = forms.CharField(max_length=12,required=True,label='Телефон',widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}))
    birth_date = forms.DateField(required=True,label='Дата рождения',widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label='Подтверждение пароля',widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'birth_date', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 14:
                raise ValidationError('Вам должно быть не менее 14 лет для регистрации')
            if age > 100:
                raise ValidationError('Пожалуйста, проверьте правильность даты рождения')
        return birth_date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise ValidationError('Введите корректный номер телефона (не менее 10 цифр)')
            if len(phone_digits) > 12:
                raise ValidationError('Номер телефона слишком длинный')
        return phone

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}))
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
