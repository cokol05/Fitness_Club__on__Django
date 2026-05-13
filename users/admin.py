from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'birth_date', 'is_trainer')


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'birth_date', 'is_trainer')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('full_name', 'email', 'phone', 'birth_date', 'is_trainer')
    ordering = ('full_name',)
    fieldsets = ((None, { 'fields': ('full_name', 'email', 'phone', 'birth_date', 'is_trainer')}), )
    add_fieldsets = ((None, { 'fields': ('full_name', 'email', 'phone', 'birth_date', 'is_trainer', 'password1', 'password2')}), )
